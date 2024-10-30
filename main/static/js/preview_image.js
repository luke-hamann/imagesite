(() => {
    var fileInputElement = document.querySelector('[name=file]');

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
    fileInputElement.addEventListener('change', () => {
        var [file] = fileInputElement.files;
        if (file) {
            previewImage.src = URL.createObjectURL(file);
        } else {
            previewImage.src = initialSource;
        }
    });
})()
