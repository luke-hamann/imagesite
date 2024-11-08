(() => {
    var deleteButton = document.querySelector('.launch-confirm-delete');
    var deleteDialog = document.querySelector('.dialog-confirm-delete');
    var deleteCancelButton = document.querySelector('.confirm-delete-cancel');

    deleteButton.addEventListener('click', (event) => {
        event.preventDefault();
        deleteDialog.showModal();
    });

    deleteCancelButton.addEventListener('click', () => {
        deleteDialog.close();
    });
})()
