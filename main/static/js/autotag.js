(() => {
    var fileInputElement = document.querySelector('[name=file]');
    var tagsInputElement = document.querySelector('[name=tags]')

    // Select or create the preview image element
    var previewImage = document.querySelector('.image-preview');
    var initialSource;
    if (previewImage) {
        initialSource = previewImage.src;
    } else {
        initialSource = '';
        previewImage = document.createElement('img');
        previewImage.classList.add('image-preview');
        fileInputElement.insertAdjacentElement('afterEnd', previewImage);
    }

    // Change the preview image on a file change
    fileInputElement.addEventListener('change', async () => {
        var [file] = fileInputElement.files;
        if (file) {
            previewImage.src = URL.createObjectURL(file);

            // Set up the loading icon
            var label = document.querySelector('[for="id_tags"]');
            var loadingIndicator = document.createElement('span');
            label.appendChild(loadingIndicator);
            var state = 0;
            var icons = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'];
            setInterval(() => {
                loadingIndicator.innerText = ' ' + icons[state];
                state++;
                state %= icons.length;
            }, 100);

            // Set up the image upload
            upload = new File([await file.arrayBuffer()], file.name, {
                'type': file.type
            });
            var data = new FormData();
            data.append('csrfmiddlewaretoken', CSRF_TOKEN);
            data.append('file', upload);

            // Post the image
            fetch('/autotag/', {
                method: 'POST',
                body: data
            })
            .then(response => response.json())
            .then(json => {
                tagsInputElement.value += json.join(' ');
                loadingIndicator.remove();
            });
        } else {
            previewImage.src = initialSource;
            suggestions = '';
        }
    });
})()