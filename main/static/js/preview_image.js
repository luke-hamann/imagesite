(() => {
    var input_element = document.querySelector('[name=file]');

    // Create the preview image element
    var preview_image = document.createElement('img');
    preview_image.id = 'upload-form-image-preview'
    input_element.insertAdjacentElement('afterEnd', preview_image);

    input_element.addEventListener('change', () => {
        var [file] = input_element.files;
        if (file) {
            preview_image.src = URL.createObjectURL(file);
        }
    });
})()
