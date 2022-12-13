$(document).ready(function () {
    let current = location.pathname.toString();
    $('#navbarTop ul li a').filter(function () {
        let link = $(this).attr('href')
        if (current.includes(link)) {
            $(this).addClass('active');
        }
    })
})
