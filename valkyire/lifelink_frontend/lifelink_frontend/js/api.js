async function apiRequest(endpoint, method = "GET", data = null) {
    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(BASE_URL + endpoint, options);
        return await response.json();
    } catch (error) {
        return { status: "error", message: "Server not connected" };
    }
}