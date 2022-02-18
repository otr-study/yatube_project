
(function ($) {

    $('.article-middle__stats-heart').on('click', function (event) {

        // Prevent default.
        event.preventDefault();
        event.stopPropagation();

        // $.get(event.target.href, function (data) {
        //     alert('1')

        // });
        $.ajax({
            url: event.target.href,
            success: function (data) {
                alert('1')

            }
        });

    })
})(jQuery);
