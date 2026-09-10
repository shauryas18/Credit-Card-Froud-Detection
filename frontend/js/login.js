document
    .getElementById("loginForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const email =
            document.getElementById("email").value;

        const password =
            document.getElementById("password").value;

        const message =
            document.getElementById("message");


        try {

            const response = await fetch(
                "/api/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );


            const data =
                await response.json();


            if (data.success) {

                message.innerHTML = `
                    <div class="alert alert-success">
                        ${data.message}
                    </div>
                `;


                setTimeout(function() {

                    window.location.href =
                        "/dashboard.html";

                }, 700);

            } else {

                message.innerHTML = `
                    <div class="alert alert-danger">
                        ${data.message}
                    </div>
                `;

            }


        } catch (error) {

            console.error(error);

            message.innerHTML = `
                <div class="alert alert-danger">
                    Server error. Please try again.
                </div>
            `;

        }

    });