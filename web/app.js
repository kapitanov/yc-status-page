function copyToClipboard(id) {
    const noPrintElements = document.querySelectorAll('.__noprint');
    noPrintElements.forEach(el => el.style.display = 'none');

    htmlToImage
        .toBlob(document.getElementById(id))
        .then(function (blob) {
            download(blob, "yc-status-page.png", "image/png");
        })
        .finally(() => {
            noPrintElements.forEach(el => el.style.display = '');
        });
}
