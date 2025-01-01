let question_bank = [];
var timestamps = [];

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Received message:", request);

  // Using Promise.resolve() to handle async operations properly
  const handleMessage = async () => {
    try {
      if (request.type === "getQuestions") {
        await send_get_question_request(request.video_url);
        timestamps = [];
        for (let item of question_bank) {
            timestamps.push(item.timestamp);
        }
        return { success: true, timestamp: timestamps };
      }      
      if (request.type === "displayQuestion") {
        await display_question(request.idx);
        return { success: true };
      }
      
      return { success: false, error: "Unknown message type" };
    } catch (error) {
      console.error("Error in message listener:", error);
      return { success: false, error: error.message };
    }
  };

  // This is crucial for handling async responses in Chrome extensions
  Promise.resolve(handleMessage())
    .then(sendResponse);

  // Return true to indicate we'll send a response asynchronously
  return true;
});

async function send_get_question_request(video_url) {
  const url = "http://127.0.0.1:5000/questions";
  
  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "link": video_url,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    question_bank = data;
    console.log("Questions fetched successfully:", question_bank);
    return question_bank;
    
  } catch (error) {
    console.error("Error fetching questions:", error);
    throw error;
  }
}

async function display_question(idx) {
  try {
    // For you to do, change question text
    document.getElementById("question").textContent = question_bank[idx].question;

    populate_options_and_check_answer(idx);
    return true;
  } catch (error) {
    console.error("Error displaying question:", error);
    throw error;
  }
}
function populate_options_and_check_answer(idx){
  const options=['answer-a','answer-b','answer-c','answer-d'];
  const continueButton = document.getElementById('continue');
  if (continueButton.style.display === "block"){
    return;
  }
  continueButton.onclick = null;
  options.forEach(function(entry){
    var element = document.getElementById(entry);
    element.style.display = "block";
    element.textContent = question_bank[idx].answers[options.indexOf(entry)];
    element.onclick = function(){
      if (question_bank[idx].correct_answer===element.textContent){
        element.style.backgroundColor = "green";

        continueButton.style.display = "block";
        continueButton.onclick = function(){
          document.getElementById("question").textContent = "Waiting for next question...";
          options.forEach(function(option_choice){

            document.getElementById(option_choice).style.display = "none";
            document.getElementById(option_choice).style.backgroundColor = null;
          })
          continueButton.style.display = "none";
          playVideo();
        }
      }
      else{
        element.style.backgroundColor = "red";
      }
      options.forEach(function(other_option){
        if (other_option!==entry){
          document.getElementById(other_option).style.backgroundColor = null;
        }
      })
    };
  })
}


function playVideo() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length === 0) {
          console.error("No active tab found");
          return;
      }

      chrome.tabs.sendMessage(tabs[0].id, { type: "playVideo" }, (response) => {
          if (response?.success) {
              console.log("Video playback started successfully");
          } else {
              console.error("Failed to play video:", response?.error);
          }
      });
  });
}
