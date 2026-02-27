window.onload = async function() {
    const user = JSON.parse(localStorage.getItem("user"));

    if (!user) {
        window.location.href = "login.html";
        return;
    }

    const result = await apiRequest("/dashboard/" + user.id);

    document.getElementById("donations").innerText = result.donations || 0;
    document.getElementById("points").innerText = result.points || 0;
    document.getElementById("status").innerText = result.status || "Eligible";
};