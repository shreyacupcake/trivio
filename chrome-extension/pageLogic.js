async function get_questions() {
  try {
    console.log("Fetching questions...");
    
    const response = await chrome.runtime.sendMessage({
      type: "getQuestions",
      video_url: window.location.href
    });

    if (!response.success) {
      throw new Error(response.error || "Failed to get questions");
    }

    console.log("Questions retrieved:", response);
    return response.questions;
  } catch (error) {
    console.error("Error in get_questions:", error);
    throw error;
  }
}

async function display_question() {
  try {
    console.log("Displaying question...");
    
    const response = await chrome.runtime.sendMessage({
      type: "displayQuestion"
    });

    if (!response.success) {
      throw new Error(response.error || "Failed to display question");
    }

    console.log("Question displayed successfully");
    return true;
  } catch (error) {
    console.error("Error in display_question:", error);
    throw error;
  }
}

async function get_and_display_questions() {
  try {
    // Wait for questions to be fetched before displaying
    await get_questions();
    // Add a small delay to ensure questions are processed
    await new Promise(resolve => setTimeout(resolve, 500));
    await display_question();
    console.log("Questions fetched and displayed successfully");
  } catch (error) {
    console.error("Error in get_and_display_questions:", error);
  }
}

get_and_display_questions();
