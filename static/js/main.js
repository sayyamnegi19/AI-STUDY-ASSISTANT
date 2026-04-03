function openModal() {
    document.getElementById("authModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("authModal").style.display = "none";
}

function showLogin() {
    document.getElementById("loginForm").style.display = "block";
    document.getElementById("registerForm").style.display = "none";
    document.getElementById("loginTab").classList.add("active");
    document.getElementById("registerTab").classList.remove("active");
}

function showRegister() {
    document.getElementById("loginForm").style.display = "none";
    document.getElementById("registerForm").style.display = "block";
    document.getElementById("loginTab").classList.remove("active");
    document.getElementById("registerTab").classList.add("active");
}

window.onclick = function(event) {
    let modal = document.getElementById("authModal");
    if (event.target === modal) {
        closeModal();
    }
}

// AUTO DISMISS FLASH
document.addEventListener("DOMContentLoaded", function () {
    const flashMessages = document.querySelectorAll(".flash-message");

    flashMessages.forEach(function (message) {
        setTimeout(function () {
            message.classList.add("flash-hide");

            setTimeout(function () {
                message.remove();
            }, 400);

        }, 4000); // 4 seconds
    });
});

const pdfInput = document.getElementById("pdf-input");
const fileName = document.getElementById("file-name");

if (pdfInput) {

    pdfInput.addEventListener("change", function () {

        if (this.files.length > 0) {
            fileName.textContent = this.files[0].name;
        } else {
            fileName.textContent = "No file selected";
        }

    });

}

setInterval(()=> {
    fetch("/update_study_time", {
        method: "POST"
    });
}, 6000);

window.addEventListener("beforeunload", function () {
    navigator.sendBeacon("/update_study_time");
});

let loaderInterval;

function showLoader(message= "Loading", dynamicMessages=[]) {
    const loader = document.getElementById("global-loader");
    const text = document.getElementById("loader-text");
    loader.classList.remove("hidden");
    text.textContent = message;

    if(loaderInterval) {
        clearInterval(loaderInterval);
    }

    if(dynamicMessages.length > 0) {
        let index = 0;
        loaderInterval = setInterval(() => {
            if (index < dynamicMessages.length-1) {
                index++;
            }
            else {
                clearInterval(loaderInterval);
                return;
            }
            text.classList.remove("loader-text-animate");
            setTimeout(() => {
                text.textContent = dynamicMessages[index];
                text.classList.add("loader-text-animate");
            },50);
        },3500);
    }
}

function hideLoader() {
    document.getElementById("global-loader").classList.add("hidden");
}

document.querySelectorAll("form").forEach(form => {

    form.addEventListener("submit", () => {
        let message = "Processing";

        if (form.classList.contains("login-form")) {
            message = "Logging in";
        }
        else if (form.classList.contains("register-form")) {
            message = "Creating account";
        }
        else if (form.classList.contains("notes-form")) {
            message = "Generating notes";
            dynamicMessages = [
                "Analyzing topic",
                "Working on it",
                "Creating notes",
                "Please wait",
                "Almost done"
            ]
        }
        else if (form.classList.contains("pdf-upload-form")) {
            message = "Processing PDF";
            dynamicMessages = [
                "Extracting text",
                "Analyzing",
                "Creating notes",
                "Please wait",
                "Almost done"
            ]
        }
        else if (form.classList.contains("quiz-topic-form")) {
            message = "Creating quiz";
            dynamicMessages = [
                "Generating questions",
                "Preparing Options",
                "Almost ready"
            ]
        }
        else if (form.classList.contains("chat-input-form")) {
            message = "Thinking";
            dynamicMessages = [
                "Understanding your question",
                "Generating response",
                "Almost done"
            ]
        }
        else if (form.classList.contains("planner-form")) {
            message = "Adding task";
        }
        showLoader(message, dynamicMessages);
    });

});

window.addEventListener("load", () => {
    const chatbox = document.getElementById("chat-messages");
    if (chatbox) {
        chatbox.scrollTop = chatbox.scrollHeight;
    }
    hideLoader();
});

const pageLoader = document.getElementById("page-loader");
document.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", function(e) {
        const href = this.getAttribute("href");

        if (!href || href.startsWith("#") || href.startsWith("javascript")) {
            return;
        }

        pageLoader.classList.remove("hidden");
    });
});

window.addEventListener("load", () => {
    pageLoader.classList.add("hidden");
})
