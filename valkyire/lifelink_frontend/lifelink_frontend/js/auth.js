async function register() {
    const userData = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value,
        blood: document.getElementById("blood").value,
        lastDonation: document.getElementById("lastDonation").value,
        password: document.getElementById("password").value
    };

    const result = await apiRequest("/register", "POST", userData);

    document.getElementById("message").innerText = result.message;
}

async function login() {
    const loginData = {
        email: document.getElementById("loginEmail").value,
        password: document.getElementById("loginPassword").value
    };

    const result = await apiRequest("/login", "POST", loginData);

    if (result.status === "success") {
        localStorage.setItem("user", JSON.stringify(result.user));
        window.location.href = "dashboard.html";
    } else {
        document.getElementById("message").innerText = result.message;
    }
}