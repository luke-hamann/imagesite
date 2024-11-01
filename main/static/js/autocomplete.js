(() => {
    var inputElement = document.querySelector('.search-box');
    var autocompleteTimeout;
    var currentValue = inputElement.value;
    var selectedIndex = -1;

    function removeAutocomplete() {
        selectedIndex = -1;
        var suggestionList = document.querySelector('#suggestionList');
        if (suggestionList != null) suggestionList.remove();
    }

    function renderAutocomplete() {
        var query = encodeURIComponent(inputElement.value);
        fetch(`/autocomplete/?q=${query}`)
        .then((response) => response.text())
        .then((text) => {
            removeAutocomplete();

            // Recreate the selection list if necessary
            var parser = new DOMParser();
            var dom = parser.parseFromString(text, 'text/html');
            var suggestionList = dom.querySelector('#suggestionList');
            var count = Number(suggestionList.getAttribute('data-count'));

            if (count == 0) return;

            inputElement.insertAdjacentElement('afterEnd', suggestionList);

            var suggestionItems =
                [...suggestionList.querySelectorAll('.suggestionItem')];

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

    inputElement.addEventListener('input', () => {
        selectedIndex = -1;
        currentValue = inputElement.value;
        clearTimeout(autocompleteTimeout);
        autocompleteTimeout = setTimeout(renderAutocomplete, 50);
    });

    inputElement.addEventListener('keydown', (event) => {
        if (!['ArrowUp', 'ArrowDown'].includes(event.key)) return;
        event.preventDefault();

        suggestionList = document.querySelector('#suggestionList');
        if (suggestionList == null) return;

        var resultElements = document.querySelectorAll('#suggestionList > div');
        var choices = [];
        for (var element of resultElements) {
            choices.push(element.innerText);
        }

        if (selectedIndex > -1) {
            var selectedElement = resultElements[selectedIndex];
            selectedElement.classList.remove('selectedSuggestion');
        }

        if (event.key == 'ArrowDown') selectedIndex++;
        else if (event.key == 'ArrowUp') selectedIndex--;
        if (selectedIndex >= choices.length) {
            selectedIndex = -1;
        } else if (selectedIndex < -1) {
            selectedIndex = choices.length - 1;
        }

        if (selectedIndex > -1) {
            inputElement.value = choices[selectedIndex];
        } else {
            inputElement.value = currentValue;
        }

        if (selectedIndex > -1) {
            var selectedElement = resultElements[selectedIndex];
            selectedElement.classList.add('selectedSuggestion');
        }

        var index = inputElement.value.length;
        inputElement.setSelectionRange(index, index);
    });
})();
