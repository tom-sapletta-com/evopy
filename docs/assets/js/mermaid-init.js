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
  // Wait a bit to ensure the page is fully loaded
  setTimeout(function() {
    // Find all code blocks with mermaid content and convert them
    convertMermaidCodeBlocks();
    
    // Try to initialize any existing mermaid diagrams
    try {
      if (typeof mermaid !== 'undefined') {
        // Force re-render all mermaid diagrams
        mermaid.init(undefined, '.mermaid');
        console.log('Mermaid diagrams initialized from mermaid-init.js');
      }
    } catch (e) {
      console.error('Error initializing mermaid from mermaid-init.js:', e);
    }
  }, 1000);
});

/**
 * Converts code blocks with mermaid syntax to mermaid diagram containers
 */
function convertMermaidCodeBlocks() {
  // Method 1: Find code blocks with class 'language-mermaid'
  document.querySelectorAll('pre code.language-mermaid').forEach(convertToMermaidDiv);
  
  // Method 2: Find code blocks with mermaid fence but missing the class
  document.querySelectorAll('pre code').forEach(function(element) {
    if (element.textContent.trim().startsWith('graph ') ||
        element.textContent.trim().startsWith('flowchart ') ||
        element.textContent.trim().startsWith('sequenceDiagram ') ||
        element.textContent.trim().startsWith('classDiagram ') ||
        element.textContent.trim().startsWith('stateDiagram ') ||
        element.textContent.trim().startsWith('gantt ') ||
        element.textContent.trim().startsWith('pie ')) {
      convertToMermaidDiv(element);
    }
  });
  
  // Method 3: Find GitHub-style rendered mermaid blocks
  document.querySelectorAll('.highlight.mermaid').forEach(function(element) {
    const div = document.createElement('div');
    div.classList.add('mermaid');
    div.textContent = element.textContent;
    element.parentElement.replaceChild(div, element);
  });
}

/**
 * Converts a code element to a mermaid div
 */
function convertToMermaidDiv(element) {
  // Create a div to hold the rendered diagram
  const div = document.createElement('div');
  div.classList.add('mermaid');
  div.textContent = element.textContent;
  
  // Replace the <pre><code> with the div
  const pre = element.parentElement;
  if (pre && pre.parentElement) {
    pre.parentElement.replaceChild(div, pre);
  }
}
