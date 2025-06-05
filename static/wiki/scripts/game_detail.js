document.addEventListener("DOMContentLoaded", function () {
  // Render Markdown content
  const markdownContent = document.getElementById("markdown-content");
  if (markdownContent && markdownContent.textContent.trim() !== "") {
    markdownContent.innerHTML = marked.parse(markdownContent.textContent);
  }

  // Handle voting
  document.getElementById("upvote-btn").addEventListener("click", function () {
    // Vote API call would go here
    console.log("Upvoted");
  });

  document
    .getElementById("downvote-btn")
    .addEventListener("click", function () {
      // Vote API call would go here
      console.log("Downvoted");
    });
});
