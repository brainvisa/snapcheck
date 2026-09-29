// Open the links to other websites in a new tab
document.addEventListener("DOMContentLoaded", () => {
  for (const link of document.querySelectorAll("a.reference.external")) {
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  }
});
