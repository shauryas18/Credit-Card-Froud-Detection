async function loadHistory() {

    try {

        const response =
            await fetch("/api/history");


        const data =
            await response.json();


        if (!response.ok) {

            window.location.href =
                "/login.html";

            return;

        }


        const table =
            document.getElementById(
                "historyTable"
            );


        table.innerHTML = "";


        if (
            !data.transactions ||
            data.transactions.length === 0
        ) {

            table.innerHTML = `

                <tr>

                    <td
                        colspan="5"
                        class="text-center text-muted">

                        No transaction history found.

                    </td>

                </tr>

            `;

            return;

        }


        data.transactions.forEach(
            function(transaction) {

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


                table.innerHTML += `

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

                            <span
                                class="badge bg-${badge}">

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

            }
        );


    } catch (error) {

        console.error(error);

    }

}


loadHistory();