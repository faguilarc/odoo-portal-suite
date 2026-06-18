/** @odoo-module **/

import { Component, onMounted, onWillStart, useState, xml } from "@odoo/owl";

/**
 * Portal Starter - Enhanced frontend interactions.
 * This module adds smooth animations, search debouncing,
 * and dynamic sidebar behavior to the portal.
 */

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Animate cards on page load
function initCardAnimations() {
    const cards = document.querySelectorAll(".portal-card");
    cards.forEach((card, index) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";
        setTimeout(() => {
            card.style.transition = "opacity 0.4s ease, transform 0.4s ease";
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, index * 100);
    });
}

// Debounced search
function initSearchDebounce() {
    const searchInput = document.querySelector('input[name="search"]');
    if (!searchInput) return;

    const form = searchInput.closest("form");
    let originalSubmit = form.onsubmit;

    searchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            // Let debounce handle it
        }
    });

    searchInput.addEventListener(
        "input",
        debounce(() => {
            if (form) {
                form.submit();
            }
        }, 500)
    );
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    initCardAnimations();
    initSearchDebounce();
});