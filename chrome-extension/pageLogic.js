
// const currentUrl = window.location.href;
// console.log(currentUrl);
// pass currentUrl to flask app and get questions


// Check if the play button exists and then click it
// if (document.querySelector('.ytp-play-button')) {
//     document.querySelector('.ytp-play-button').click();
// } else {
//   console.log("Play button not found.");
// }


async function get_questions() {
  console.log("generating questions...")

  url = `http://127.0.0.1:5000/questions`;

  console.log(window.location.href)
  await fetch(url, {
    method: "GET", // Specify the method
    headers: {
      "Content-Type": "application/json", // Specify the content type
      "link": window.location.href,
    },
  })
    .then((response) => {
      if (response.ok) {
        return response.json(); // or response.text() if the server sends non-JSON response
      }
      throw new Error("Network response was not ok.");
    })
    .then((data) => {
      // process the data here and return it in a format you can store and use to play/pause
      // at the timestamps and display questions and answers.
      console.log("Success:", data);

    })
    .catch((error) => {
      console.error("Error:", error); // Handling errors
    });
}

get_questions();