const navigationBar = $("#navbar");

document.onscroll = () => {
    const titleHeight = parseInt($(".titleContainer").css("height"));

    if (titleHeight > window.pageYOffset){
        navigationBar.css("top", -window.pageYOffset);
    } else {
        navigationBar.css("top", -titleHeight);
    }

}