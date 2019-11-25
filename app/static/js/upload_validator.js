function init() {
    uploadValidate();
}

function uploadValidate() {
    button = document.getElementById('btn_upload')
    file_span = document.getElementById('upload-file-info')
    span = document.createElement("span");
    span.style = "color: red";
    span.innerHTML = "   !Only pdf file can be uploaded!"
    if (button) {
        button.addEventListener('click', e => {
            filename = file_span.innerHTML;

            if (filename.split('.').pop() != 'pdf'){
                e.preventDefault();
                file_span.appendChild(span)
            }
        })
    }
}