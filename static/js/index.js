function zoomin(id){
    var myImg = document.getElementById(id);
    var currWidth = myImg.clientWidth;
    if(currWidth == 200){
        myImg.style.width =  "500px";
    } else if(currWidth == 500){
        myImg.style.width = "200px";
    } else {
        return
    }
}