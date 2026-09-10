async function loadDashboard() {

    try {

        const userResponse =
            await fetch("/api/user");


        const userData =
            await userResponse.json();


        if (!userData.logged_in) {

            window.location.href =
                "/login.html";

            return;

        }


        document.getElementById(
            "welcomeUser"
        ).textContent =
            "Hello, " +
            userData.user.name;


        const response =
            await fetch("/api/dashboard");


        const data =
            await response.json();


        if (!data.success) {

            window.location.href =
                "/login.html";

            return;

        }


        document.getElementById(
            "totalTransactions"
        ).textContent =
            data.statistics.total;


        document.getElementById(
            "fraudTransactions"
        ).textContent =
            data.statistics.fraud;


        document.getElementById(
            "legitimateTransactions"
        ).textContent =
            data.statistics.legitimate;


        document.getElementById(
            "fraudPercentage"
        ).textContent =
            data.statistics.fraud_percentage +
            "%";


        const tbody =
            document.getElementById(
                "recentTransactions"
            );


        tbody.innerHTML = "";


        if (data.recent.length === 0) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="5"
                        class="text-center text-muted">
                        No transactions found.
                    </td>
                </tr>
            `;

            return;

        }


        data.recent.forEach(function(transaction) {

            const badge =
                transaction.prediction === "Fraud"
                ? "danger"
                : "success";


            const probability =
                transaction.probability !== null
                ? (
                    transaction.probability * 100
                  ).toFixed(2) + "%"
                : "N/A";


            tbody.innerHTML += `

                <tr>

                    <td>
                        ${transaction.id}
                    </td>

                    <td>
                        ₹${Number(
                            transaction.amount
                        ).toFixed(2)}
                    </td>

                    <td>

                        <span class="badge bg-${badge}">

                            ${transaction.prediction}

                        </span>

                    </td>

                    <td>
                        ${probability}
                    </td>

                    <td>
                        ${transaction.created_at}
                    </td>

                </tr>

            `;

        });


    } catch (error) {

        console.error(error);

    }

}


document
    .getElementById("logoutBtn")
    .addEventListener(
        "click",
        async function() {

            await fetch(
                "/api/logout",
                {
                    method: "POST"
                }
            );


            window.location.href =
                "/login.html";

        }
    );


loadDashboard();