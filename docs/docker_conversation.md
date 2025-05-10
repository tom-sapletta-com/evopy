# Kontynuacja konwersacji w interfejsie Docker

## Wprowadzenie

Evopy umożliwia teraz kontynuację konwersacji po przejściu na stronę szczegółów kontenera Docker. Ta funkcjonalność pozwala użytkownikom na dalszą interakcję z systemem bez konieczności powrotu do głównego interfejsu konwersacji, co znacznie poprawia płynność pracy i doświadczenie użytkownika.

## Opis funkcjonalności

### 1. Interfejs kontynuacji konwersacji

Na stronie szczegółów kontenera Docker (`/docker/<task_id>`) dodano formularz, który umożliwia użytkownikowi wprowadzenie nowego promptu i kontynuację konwersacji. Formularz zawiera:

- Pole tekstowe do wprowadzenia nowego promptu
- Przycisk do wysłania promptu
- Opcję uruchomienia kodu w kontenerze Docker (domyślnie włączona)

### 2. Przepływ danych

Proces kontynuacji konwersacji przebiega następująco:

1. Użytkownik wprowadza nowy prompt w formularzu na stronie szczegółów kontenera Docker.
2. System przetwarza prompt za pomocą modułu `text2python`.
3. Generowany jest nowy kod Python na podstawie promptu.
4. Kod jest wykonywany w kontenerze Docker (jeśli opcja jest włączona).
5. Tworzony jest nowy kontener Docker i rejestrowane jest nowe zadanie.
6. Użytkownik jest przekierowywany do strony szczegółów nowego zadania Docker.

### 3. Integracja z modułem docker_tasks_store

Moduł `docker_tasks_store` został rozszerzony o dodatkowe informacje związane z kontynuacją konwersacji:

- `web_interface_url` - pełny URL do strony szczegółów kontenera Docker
- `continue_url` - URL do endpointu kontynuacji konwersacji
- `continue_info` - informacja o możliwości kontynuacji konwersacji

## Implementacja

### 1. Endpoint kontynuacji konwersacji

W module `server.py` dodano nowy endpoint `/docker/<task_id>/continue`, który obsługuje kontynuację konwersacji:

```python
@app.route('/docker/<string:task_id>/continue', methods=['POST'])
def docker_task_continue(task_id):
    """Kontynuacja konwersacji dla zadania Docker"""
    # Pobierz prompt z formularza
    prompt = request.form.get('prompt')
    use_sandbox = request.form.get('use_sandbox') == 'true'
    
    # Dynamicznie importuj moduł text2python
    module_path = os.path.join(MODULES_DIR, 'text2python', 'text2python.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Inicjalizacja konwertera i generowanie kodu
    converter = module.Text2Python()
    result = converter.process(prompt)
    
    # Wykonaj kod w piaskownicy Docker
    new_code = result.get("code", "")
    execution_result = converter.execute_code(new_code, use_sandbox=use_sandbox)
    
    # Utwórz nowe zadanie Docker
    new_task_id = str(uuid.uuid4())
    container_id = execution_result.get("container_name", f"evopy-sandbox-{new_task_id}")
    
    # Zarejestruj nowe zadanie Docker
    register_docker_container(
        task_id=new_task_id,
        container_id=container_id,
        code=new_code,
        output=execution_result,
        is_service=False,
        user_prompt=prompt,
        container_exists=True
    )
    
    # Przekieruj do nowego zadania Docker
    return redirect(url_for('docker_task_details', task_id=new_task_id))
```

### 2. Formularz kontynuacji konwersacji

W szablonie `docker_task.html` dodano formularz do wprowadzania nowych promptów:

```html
<div class="mt-4">
    <h5>Kontynuuj konwersację</h5>
    <form id="promptForm" action="/docker/{{ task_id }}/continue" method="post" class="mb-3">
        <div class="form-group">
            <textarea class="form-control" id="prompt" name="prompt" rows="3" placeholder="Wprowadź nowy prompt..."></textarea>
        </div>
        <div class="d-flex justify-content-between align-items-center mt-2">
            <button type="submit" class="btn btn-primary">
                <i class="fas fa-paper-plane me-2"></i> Wyślij
            </button>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" value="true" id="use_sandbox" name="use_sandbox" checked>
                <label class="form-check-label" for="use_sandbox">
                    Uruchom w kontenerze Docker
                </label>
            </div>
        </div>
    </form>
</div>
```

### 3. Rozszerzenie modułu docker_tasks_store

W module `docker_tasks_store.py` dodano nowe pola do słownika zadań Docker:

```python
# Generuj linki do kontenera Docker
container_link = f"/docker/{task_id}"
web_interface_url = f"http://localhost:5000/docker/{task_id}"
continue_url = f"http://localhost:5000/docker/{task_id}/continue"
continue_info = f"Możesz kontynuować konwersację pod adresem: {web_interface_url}"

DOCKER_TASKS[task_id] = {
    # ... istniejące pola ...
    "container_link": container_link,
    "web_interface_url": web_interface_url,
    "continue_url": continue_url,
    "continue_info": continue_info
}
```

## Korzyści

1. **Płynność pracy** - użytkownik może kontynuować konwersację bez konieczności powrotu do głównego interfejsu.
2. **Lepsza organizacja** - wszystkie zadania Docker związane z konwersacją są powiązane ze sobą.
3. **Łatwiejsze testowanie** - możliwość szybkiego testowania różnych wariantów kodu.
4. **Lepsze doświadczenie użytkownika** - bardziej intuicyjny i spójny interfejs.

## Ograniczenia i przyszłe ulepszenia

1. **Historia konwersacji** - dodanie widoku historii konwersacji na stronie szczegółów kontenera Docker.
2. **Powiązanie zadań** - lepsze powiązanie zadań Docker z konwersacją, z której pochodzą.
3. **Interfejs użytkownika** - dalsze ulepszenia interfejsu użytkownika dla kontynuacji konwersacji.
4. **Wsparcie dla innych modułów** - rozszerzenie funkcjonalności na inne moduły konwersji (text2sql, shell2text, itp.).
