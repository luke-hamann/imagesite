(() => {
    var inputElement = document.querySelector('[name=tags]');
    var autocompleteTimeout;
    var currentValue = inputElement.value;
    var selectedIndex = -1;

    function renderAutocomplete() {
        var query = encodeURIComponent(inputElement.value);
        fetch(`/autocomplete/?q=${query}`)
        .then((response) => response.text())
        .then((text) => {
            // Delete the suggestion list if it exists
            var suggestionList = document.querySelector('#suggestionList');
            if (suggestionList != null) suggestionList.remove();

            // Recreate the selection list if necessary
            var parser = new DOMParser();
            var dom = parser.parseFromString(text, 'text/html');
            suggestionList = dom.querySelector('#suggestionList');
            var count = Number(suggestionList.getAttribute('data-count'));

            if (count == 0) return;

            inputElement.insertAdjacentElement('afterEnd', suggestionList);

            var suggestionItems =
                [...suggestionList.querySelectorAll('.suggestionItem')];

            for (var item of suggestionItems) {
                item.addEventListener('mouseover', (event) => {
                    currentTarget = event.currentTarget;

                    if (selectedIndex > -1) {
                        var selected = document.querySelector('.selectedSuggestion');
                        selected.classList.remove('selectedSuggestion');
                    }

                    selectedIndex = Number(currentTarget.getAttribute('data-index'));
                    currentTarget.classList.add('selectedSuggestion');
                });

                item.addEventListener('click', (event) => {
                    inputElement.value = event.currentTarget.innerText;
                    currentValue = inputElement.value;
                    renderAutocomplete();
                    inputElement.focus();
                });
            }
        });
    }

    inputElement.addEventListener('focus', renderAutocomplete);
    
    inputElement.addEventListener('blur', () => {
        if (document.querySelector('#suggestionList:hover') != null) return;

        selectedIndex = -1;
        var suggestionList = document.querySelector('#suggestionList');
        if (suggestionList != null) {
            suggestionList.remove();
        }
    });

    inputElement.addEventListener('input', () => {
        selectedIndex = -1;
        currentValue = inputElement.value;
        clearTimeout(autocompleteTimeout);
        autocompleteTimeout = setTimeout(renderAutocomplete, 10);
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
