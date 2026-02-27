async function createRequest() {
    const requestData = {
        patientName: document.getElementById("patientName").value,
        blood: document.getElementById("bloodNeeded").value,
        hospital: document.getElementById("hospital").value,
        location: document.getElementById("location").value
    };

    const result = await apiRequest("/create-request", "POST", requestData);

    document.getElementById("message").innerText = result.message;
}