
(function ($) {

    $('.article-middle__stats-heart').on('click', function (event) {

        // Prevent default.
        event.preventDefault();
        event.stopPropagation();

        fetch(event.target.href)
            .then((response) => {
                if (response.ok)
                    if (response.redirected) {
                        window.location.replace(response.url.split('?')[0]);
                    }
                    else
                        return response.json();
            })
            .then((data) => {
                let hearts = $('#article_heart_' + data.post_id);
                if (hearts.length) {
                    hearts[0].innerText = ` ${data.count}`;
                    if (data.result)
                        hearts.addClass('article-middle__stats-heart_solid')
                    else
                        hearts.removeClass('article-middle__stats-heart_solid')
                }
            });

    })
})(jQuery);
