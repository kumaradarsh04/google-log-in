async function handleCredentialResponse(response) {

    console.log("Google gave us an ID token.");


    // ----------------------------------------
    // Send token to backend
    // ----------------------------------------

    const result = await fetch("/auth/google", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            credential: response.credential
        })

    });


    if (!result.ok) {

        console.error(
            "Google token verification failed."
        );

        alert("Authentication failed.");

        return;
    }


    console.log(
        "Google token verified successfully."
    );


    // The backend has now created
    // our application session.


    await loadCurrentUser();
}


// ==========================================
// LOAD CURRENT USER
// ==========================================

async function loadCurrentUser() {

    console.log(
        "Checking existing application session..."
    );


    const result = await fetch("/auth/me");


    // ----------------------------------------
    // No valid session
    // ----------------------------------------

    if (!result.ok) {

        console.log(
            "No active application session."
        );

        showLogin();

        return;
    }


    // ----------------------------------------
    // Valid session
    // ----------------------------------------

    const data = await result.json();

    console.log(
        "Existing session found!"
    );

    console.log(data);


    showUser(data.user);
}


// ==========================================
// SHOW USER
// ==========================================

function showUser(user) {

    document.getElementById(
        "user-name"
    ).textContent =
        "Name: " + user.name;


    document.getElementById(
        "user-email"
    ).textContent =
        "Email: " + user.email;


    const profilePicture =
        document.getElementById(
            "profile-picture"
        );


    if (user.picture) {

        profilePicture.src =
            user.picture;

    }


    document.getElementById(
        "login-section"
    ).style.display = "none";


    document.getElementById(
        "user-section"
    ).style.display = "block";
}


// ==========================================
// SHOW LOGIN
// ==========================================

function showLogin() {

    document.getElementById(
        "login-section"
    ).style.display = "block";


    document.getElementById(
        "user-section"
    ).style.display = "none";
}


// ==========================================
// LOGOUT
// ==========================================

async function logout() {

    const result = await fetch(
        "/auth/logout",
        {
            method: "POST"
        }
    );


    if (result.ok) {

        console.log(
            "Logged out successfully."
        );

        showLogin();

    }

}


// ==========================================
// CHECK SESSION WHEN PAGE LOADS
// ==========================================

window.addEventListener(
    "DOMContentLoaded",
    loadCurrentUser
);
