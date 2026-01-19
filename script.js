async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const mode = document.getElementById("mode").value;
  const error = document.getElementById("error");

  const response = await fetch("users.txt");
  const text = await response.text();

  const users = text.trim().split("\n");

  for (let user of users) {
    const [u, p, role] = user.split(",");

    if (u === username && p === password && role === mode) {
      if (role === "user") {
        window.location.href = "usermode/static/index.html";
      } else {
        window.location.href = "learningmode/static/index.html";
      }
      return;
    }
  }

  error.textContent = "Invalid login or mode";
}
