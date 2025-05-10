import os
import requests
import openpyxl

def prepare_excel(filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["x", "y"])
    for i in range(10):
        ws.append([i, i*i])
    wb.save(filename)

def test_e2e_generate_plot():
    excel_file = "test_e2e_plot.xlsx"
    prepare_excel(excel_file)
    try:
        url = "http://127.0.0.1:5000/run"
        data = {"task": "stwórz wykres z pliku excel"}
        resp = requests.post(url, json=data)
        assert resp.status_code == 200, f"API error: {resp.text}"
        out = resp.json()
        assert "download_url" in out, f"No download_url in response: {out}"
        download_url = f"http://127.0.0.1:5000{out['download_url']}"
        plot_resp = requests.get(download_url)
        assert plot_resp.status_code == 200, f"Download failed: {plot_resp.text}"
        assert plot_resp.headers["content-type"].startswith("image/"), "Not an image file"
        with open("e2e_downloaded_plot.png", "wb") as f:
            f.write(plot_resp.content)
        print("[E2E] Test zakończony sukcesem: wykres pobrany.")
    finally:
        if os.path.exists(excel_file):
            os.remove(excel_file)
        if os.path.exists("e2e_downloaded_plot.png"):
            os.remove("e2e_downloaded_plot.png")

if __name__ == "__main__":
    test_e2e_generate_plot()
