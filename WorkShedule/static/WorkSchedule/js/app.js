$(function () {

    $(".date").each(function (index, element) {
        $(element).on("click", function (event) {
            $(element).css('background-color', 'red');
        })

    });







});

// $(document).on('submit', "#timesheet",function(event){
//     event.preventDefault();
//
//     $.ajax({
//         method: "POST",
//         url: 'add_schedule',
//         data:{
//             days:$('.workday').val(),
//             user:$('#userId').val()
//         },
//         success:function() {
//             alert("COs")
//
//         }
//     });
// })

