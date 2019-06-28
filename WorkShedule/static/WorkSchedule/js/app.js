$(function () {

    $(".date").each(function (index, element) {
        $(element).on("click", function (event) {
            $(element).css('background-color', 'red');
        })

    });


    $(".alert_button").on('click', function () {
        $(".dropdown-ul").toggleClass('active');

    });



});

