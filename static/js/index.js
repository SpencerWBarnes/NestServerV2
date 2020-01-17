function zoomin(id) {
    var vids = ["vid1", "vid2", "vid3", "vid4", "vid5", "vid6"];
    var myImg = document.getElementById(id);
    var currWidth = myImg.clientWidth;
    if (currWidth == 200) {
        myImg.style.width = "500px";
        hideOtherVideos(id);
    } else if (currWidth == 500) {
        showAllVideos();
        for (var i = 0; i < vids.length; i++) {
            document.getElementById(vids[i]).style = "width:200px";
        }
    } else {
        return;
    }
}

function hideOtherVideos(id) {
    var vids = ["vid1", "vid2", "vid3", "vid4", "vid5", "vid6"];
    for (var i = 0; i < vids.length; i++) {
        if (vids[i] !== id) {
            document.getElementById(vids[i]).style = "display:none";
        }
    }
}

function showAllVideos() {
    var vids = ["vid1", "vid2", "vid3", "vid4", "vid5", "vid6"];
    for (var i = 0; i < vids.length; i++) {
        document.getElementById(vids[i]).style = "display:block";
    }
}
