lazyload();
var selected_game = null;

function uiSelectGame(game) {
    var select_toggle = "bg-light border-primary text-primary";
    if (selected_game !== null)
        selected_game.removeClass(select_toggle);

    selected_game = game;
    selected_game.addClass(select_toggle);
}

function uiUpdateSidebar(game) {
    var game_id = game.attr("game-id");
    var fields = ["Developer", "Publisher", "Genre", "Series", "PlayMode", "Status", "Source", "Hide", "Notes"];
    $.getJSON("/game/" + game_id + "/info", function(data) {
        $("#game-title").text(data['Title']);
        var ui_game_meta = $("#game-meta");
        ui_game_meta.empty();
        for (var i = 0; i < fields.length; i++) {
            if (data[fields[i]] === null) {
                continue;
            }
            ui_game_meta.append($("<li></li>").text(fields[i] + ":   " + data[fields[i]]));
            $("#game-screenshot-block").removeClass("d-none");
            $("#game-launch-btn").removeClass("d-none");
            $("#game-screenshot-img").attr("src", "/game/" + game_id + "/screenshot");
        }

    })

}

$(".game-card").click(function() {
    uiSelectGame($(this))
    uiUpdateSidebar($(this))
});

$("#game-launch-btn").click(function() {
    $.get({
        url: "/game/" + selected_game.attr("game-id") + "/launch",
        dataType: "text/plain"
    });
});