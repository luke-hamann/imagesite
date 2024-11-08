(() => {
    const SEARCH_BOX = '.search-box';
    const SUGGESTION_LIST = '#suggestionList';
    const SUGGESTION_ITEMS = '.suggestionItem';
    const SELECTED_SUGGESTION = 'selectedSuggestion';

    // Initialize the variables
    var inputElement = document.querySelector(SEARCH_BOX);
    var autocompleteTimeout;
    var currentValue = inputElement.value;
    var selectedIndex = -1;

    /**
     * Remove the autocompletion menu
     */
    function removeAutocomplete() {
        selectedIndex = -1;
        var suggestionList = document.querySelector(SUGGESTION_LIST);
        if (suggestionList != null) suggestionList.remove();
    }

    /**
     * Render the autocompletion menu
     */
    function renderAutocomplete() {
        var query = encodeURIComponent(inputElement.value);
        fetch(`/autocomplete/?q=${query}`)
        .then((response) => response.text())
        .then((text) => {
            removeAutocomplete();

            // Rebuild the menu
            var parser = new DOMParser();
            var dom = parser.parseFromString(text, 'text/html');
            var suggestionList = dom.querySelector(SUGGESTION_LIST);
            var count = Number(suggestionList.getAttribute('data-count'));

            if (count == 0) return;

            inputElement.insertAdjacentElement('afterEnd', suggestionList);

            var suggestionItems =
                [...suggestionList.querySelectorAll(SUGGESTION_ITEMS)];

            // Add a click event to each suggestion item
            for (var item of suggestionItems) {
                item.addEventListener('click', (event) => {
                    selectedIndex = -1;
                    inputElement.value = event.currentTarget.innerText + ' ';
                    currentValue = inputElement.value;
                    renderAutocomplete();
                    inputElement.focus();
                });
            }
        });
    }

    inputElement.addEventListener('focus', renderAutocomplete);

    inputElement.addEventListener('blur', () => {
        // Timeout is needed so click events register on suggestion items
        setTimeout(removeAutocomplete, 100);
    });

    /**
     * Render the autocomplete menu everytime the user changes the search text
     */
    inputElement.addEventListener('input', () => {
        selectedIndex = -1;
        currentValue = inputElement.value;

        // Debounce the input events
        clearTimeout(autocompleteTimeout);
        autocompleteTimeout = setTimeout(renderAutocomplete, 50);
    });

    /**
     * Manage keyboard navigation through the suggestion list
     */
    inputElement.addEventListener('keydown', (event) => {
        if (!['ArrowUp', 'ArrowDown'].includes(event.key)) return;
        event.preventDefault();

        suggestionList = document.querySelector(SUGGESTION_LIST);
        if (suggestionList == null) return;

        var suggestionElements =
            [...document.querySelectorAll(SUGGESTION_ITEMS)];

        // Remove selection from previously selected element
        if (selectedIndex > -1) {
            var selectedElement = suggestionElements[selectedIndex];
            selectedElement.classList.remove(SELECTED_SUGGESTION);
        }

        // Compute the new selection index
        selectedIndex += (event.key == 'ArrowDown' ? 1 : -1);

        if (selectedIndex >= suggestionElements.length) {
            selectedIndex = -1;
        } else if (selectedIndex < -1) {
            selectedIndex = suggestionElements.length - 1;
        }

        // Update the input field and selected suggestion
        if (selectedIndex > -1) {
            var selectedElement = suggestionElements[selectedIndex];
            selectedElement.classList.add(SELECTED_SUGGESTION);
            inputElement.value = selectedElement.innerText;
        } else {
            inputElement.value = currentValue;
        }

        var index = inputElement.value.length;
        inputElement.setSelectionRange(index, index);
    });
})();
