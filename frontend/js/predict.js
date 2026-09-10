document
    .getElementById("predictionForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();


        const message =
            document.getElementById("message");

        const result =
            document.getElementById("result");


        message.innerHTML = "";


        const fields = [

            "Time",

            "V1",
            "V2",
            "V3",
            "V4",
            "V5",
            "V6",
            "V7",
            "V8",
            "V9",
            "V10",
            "V11",
            "V12",
            "V13",
            "V14",
            "V15",
            "V16",
            "V17",
            "V18",
            "V19",
            "V20",
            "V21",
            "V22",
            "V23",
            "V24",
            "V25",
            "V26",
            "V27",
            "V28",

            "Amount"

        ];


        const transaction = {};


        fields.forEach(function(field) {

            transaction[field] =
                Number(
                    document.getElementById(field).value
                );

        });


        try {

            result.innerHTML = `
                <div class="alert alert-info">
                    Analyzing transaction...
                </div>
            `;


            const response =
                await fetch(
                    "/api/predict",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(transaction)
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                result.innerHTML = `
                    <div class="alert alert-danger">
                        ${data.message}
                    </div>
                `;

                return;

            }


            if (data.success) {

                const probability =
                    data.probability !== null
                    ? (
                        data.probability * 100
                      ).toFixed(2) + "%"
                    : "N/A";


                if (data.prediction === "Fraud") {

                    result.innerHTML = `

                        <div class="alert alert-danger p-4">

                            <h3 class="fw-bold">
                                ⚠ Fraud Detected
                            </h3>

                            <p>
                                ${data.message}
                            </p>

                            <hr>

                            <strong>
                                Fraud Probability:
                            </strong>

                            ${probability}

                        </div>

                    `;

                } else {

                    result.innerHTML = `

                        <div class="alert alert-success p-4">

                            <h3 class="fw-bold">
                                ✓ Legitimate Transaction
                            </h3>

                            <p>
                                ${data.message}
                            </p>

                            <hr>

                            <strong>
                                Fraud Probability:
                            </strong>

                            ${probability}

                        </div>

                    `;

                }

            }


        } catch (error) {

            console.error(error);

            result.innerHTML = `

                <div class="alert alert-danger">

                    Unable to connect to server.

                </div>

            `;

        }

    });