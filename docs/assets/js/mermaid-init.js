/**
 * Mermaid Initialization Script for Evopy Documentation
 * 
 * This script initializes Mermaid diagrams on all pages.
 * It looks for both fenced code blocks with language-mermaid class
 * and div elements with mermaid class.
 * 
 * Copyright 2025 Tom Sapletta
 * Licensed under the Apache License, Version 2.0
 */

document.addEventListener("DOMContentLoaded", function() {
  // Initialize mermaid with configuration
  mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    flowchart: { 
      useMaxWidth: true, 
      htmlLabels: true,
      curve: 'basis'
    },
    sequence: {
      diagramMarginX: 50,
      diagramMarginY: 10,
      boxMargin: 10,
      noteMargin: 10,
      messageMargin: 35
    }
  });
  
  // Find all code blocks with class 'language-mermaid' and render them
  document.querySelectorAll('pre code.language-mermaid').forEach(function(element) {
    // Create a div to hold the rendered diagram
    const div = document.createElement('div');
    div.classList.add('mermaid');
    div.textContent = element.textContent;
    
    // Replace the <pre><code> with the div
    const pre = element.parentElement;
    pre.parentElement.replaceChild(div, pre);
  });
  
  // Initialize mermaid
  mermaid.init(undefined, '.mermaid');
  
  // Add a class to indicate that mermaid has been initialized
  document.body.classList.add('mermaid-initialized');
  
  // Log success message
  console.log('Mermaid diagrams initialized successfully');
});
