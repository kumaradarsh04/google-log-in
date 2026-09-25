async function handleCredentialResponse(response) {

    console.log("Google gave us an ID token.");

    const idToken = response.credential;


    // ----------------------------------------
    // Send token to our backend
    // ----------------------------------------

    const result = await fetch("/auth/google", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            credential: idToken
        })

    });


    // ----------------------------------------
    // Backend rejected token
    // ----------------------------------------

    if (!result.ok) {

        console.error("Google token verification failed.");

        alert("Authentication failed.");

        return;
    }


    // ----------------------------------------
    // Backend accepted token
    // ----------------------------------------

    const data = await result.json();


    console.log("Backend verified the user:");
    console.log(data);


    const user = data.user;


    // ----------------------------------------
    // Display verified information
    // ----------------------------------------

    document.getElementById("user-name").textContent =
        "Name: " + user.name;

    document.getElementById("user-email").textContent =
        "Email: " + user.email;


    const profilePicture =
        document.getElementById("profile-picture");


    if (user.picture) {

        profilePicture.src = user.picture;

    }


    // ----------------------------------------
    // Change UI
    // ----------------------------------------

    document.getElementById("login-section")
        .style.display = "none";

    document.getElementById("user-section")
        .style.display = "block";


    console.log("✅ Authentication successful!");
}


function logout() {

    document.getElementById("login-section")
        .style.display = "block";

    document.getElementById("user-section")
        .style.display = "none";


    google.accounts.id.disableAutoSelect();

    console.log("Logged out.");

}