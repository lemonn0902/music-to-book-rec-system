// Function to toggle between login and register forms
function toggleForms() {
    console.log("Toggle function called"); // Debugging

    const formTitle = document.getElementById("form-title");
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const toggleLink = document.getElementById("toggle-to-register");

    if (loginForm.style.display === "none") {
        // Switch to Login
        formTitle.textContent = "Login";
        loginForm.style.display = "block";
        registerForm.style.display = "none";
        toggleLink.textContent = "Don't have an account? Register here";
    } else {
        // Switch to Register
        formTitle.textContent = "Register";
        loginForm.style.display = "none";
        registerForm.style.display = "block";
        toggleLink.textContent = "Already have an account? Login here";
    }
}

// Ensure DOM is fully loaded before adding event listeners
document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded"); // Debugging

    // Toggle between forms
    const toggleLink = document.getElementById("toggle-to-register");
    if (toggleLink) {
        toggleLink.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent default anchor behavior
            toggleForms();
        });
        console.log("Event listener attached to toggle link"); // Debugging
    } else {
        console.error("Toggle link not found!"); // Debugging
    }

    // Handle login form submission
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", function (e) {
            e.preventDefault(); // Prevent default form submission
            console.log("Login form submitted"); // Debugging

            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries()); // Convert to object

            fetch("/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email: data.email, password: data.password }),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log("Login Response:", data); // Debugging
                    if (data.access_token) {
                        localStorage.setItem("access_token", data.access_token); // Store token
                        window.location.href = "/home"; // Redirect to home page
                    } else {
                        alert(data.detail || "Invalid login credentials. Please try again.");
                    }
                })
                
                .catch((error) => {
                    console.error("Login Error:", error);
                    alert("Login failed. Please try again.");
                });
                
        });
    } else {
        console.error("Login form not found!");
    }

    // Handle registration form submission
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", function (e) {
            e.preventDefault(); // Prevent default form submission
            console.log("Register form submitted"); // Debugging

            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries()); // Convert to object

            fetch("/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log("Register Response:", data); // Debugging
                    if (data.message) {
                        alert(data.message); // Show success message
                        toggleForms(); // Switch to login form after registration
                    } else {
                        alert("Registration failed. Please check your details.");
                    }
                })
                .catch((error) => {
                    console.error("Registration Error:", error);
                    alert("Registration failed. Please try again.");
                });
        });
    } else {
        console.error("Register form not found!");
    }
});
