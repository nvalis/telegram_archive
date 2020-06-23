function as_time(d) {
  return String(Math.floor(d / 60)).padStart(2, '0') + ":" + String(Math.floor(d % 60)).padStart(2, '0');
}

// Audio player initialisation
document.addEventListener('DOMContentLoaded', function() {
  for (let element of document.querySelectorAll("audio")) {
    element.addEventListener("timeupdate", function(e) {
      let percentage = e.target.currentTime / e.target.duration * 100;
      e.target.parentNode.querySelector(".waveform.blue").setAttribute("style", "width: " + percentage + "%");
      e.target.parentNode.querySelector("time").innerHTML = as_time(e.target.duration - e.target.currentTime);
    });
  }
  for (var element of document.querySelectorAll(".button.play")) {
    element.addEventListener("click", function(e) {
      var audio = document.querySelector("#" + e.target.getAttribute("data-audio") + " audio");
      if (audio.paused) {
        audio.play();
        e.target.setAttribute("class", e.target.getAttribute("class") + " playing");
      } else {
        audio.pause();
        e.target.setAttribute("class", e.target.getAttribute("class").replace("playing").trim());
      }
    });
  }
}, false);
