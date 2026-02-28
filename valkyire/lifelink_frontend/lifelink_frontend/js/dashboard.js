window.onload = async function() {
    const user = JSON.parse(localStorage.getItem("user"));

    if (!user) {
        window.location.href = "login.html";
        return;
    }

    console.log("Fetching dashboard for user:", user.id);
    
    try {
        const result = await apiRequest("/dashboard/" + user.id);
        console.log("Dashboard result:", result);
        
        document.getElementById("donations").innerText = result.donations || 0;
        document.getElementById("points").innerText = result.points || 0;
        document.getElementById("status").innerText = result.status || "Eligible";
    } catch (error) {
        console.error("Dashboard error:", error);
        document.getElementById("donations").innerText = "Error";
        document.getElementById("points").innerText = "Error";
        document.getElementById("status").innerText = "Error";
    }
};