const navigationBar = $("#navbar");

$("#contentBox").css("top", $("#navbar").css("height")); //Sets the content below the navbar.

document.onscroll = () => {
    const titleHeight = parseInt($(".titleContainer").css("height"));
    const navbarHeigt = parseInt($("#navbar").css("height"));
    const contentBx = $("#contentBox");
    if (titleHeight > window.pageYOffset){
        navigationBar.css("top", 0);
        navigationBar.css("position", "absolute");
    } else {
        navigationBar.css("top", -titleHeight);
        navigationBar.css("position", "fixed");
    }
    contentBx.css("top", navbarHeigt);

}