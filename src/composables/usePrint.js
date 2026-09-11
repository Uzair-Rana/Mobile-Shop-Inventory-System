export function usePrint() {
  function printDocument(elementId, title = 'Document') {
    const element = document.getElementById(elementId)
    if (!element) {
      console.error(`Element with id "${elementId}" not found`)
      return
    }

    const printWindow = window.open('', '', 'width=900,height=600')
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>${title}</title>
          <style>
            * {
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
              line-height: 1.5;
              color: #1f2937;
              background: white;
              padding: 20px;
            }
            @media print {
              body {
                padding: 0;
              }
            }
            .print-content {
              max-width: 900px;
              margin: 0 auto;
              background: white;
            }
            table {
              width: 100%;
              border-collapse: collapse;
              margin: 20px 0;
            }
            th, td {
              padding: 12px;
              text-align: left;
              border-bottom: 1px solid #e5e7eb;
            }
            th {
              background-color: #f3f4f6;
              font-weight: 600;
              font-size: 13px;
              text-transform: uppercase;
              letter-spacing: 0.5px;
            }
            td {
              font-size: 14px;
            }
            td.text-right, th.text-right {
              text-align: right;
            }
            .header {
              margin-bottom: 30px;
              border-bottom: 2px solid #1f2937;
              padding-bottom: 20px;
            }
            .header h1 {
              font-size: 24px;
              margin-bottom: 5px;
            }
            .header-info {
              display: grid;
              grid-template-columns: 1fr 1fr 1fr;
              gap: 20px;
              font-size: 13px;
              color: #6b7280;
              margin-top: 10px;
            }
            .footer {
              margin-top: 30px;
              padding-top: 20px;
              border-top: 1px solid #e5e7eb;
              font-size: 12px;
              color: #6b7280;
              text-align: center;
            }
            .totals {
              margin: 30px 0;
              display: flex;
              justify-content: flex-end;
            }
            .totals-table {
              width: 300px;
            }
            .totals-table td {
              padding: 8px 12px;
              border: none;
            }
            .totals-table .label {
              text-align: left;
              color: #6b7280;
              font-size: 13px;
            }
            .totals-table .value {
              text-align: right;
              font-weight: 500;
              font-size: 14px;
            }
            .totals-table .total-row {
              border-top: 2px solid #1f2937;
              border-bottom: 2px solid #1f2937;
              font-weight: 600;
              font-size: 16px;
            }
            .badge {
              display: inline-block;
              padding: 4px 8px;
              border-radius: 4px;
              font-size: 12px;
              font-weight: 600;
            }
            .badge-paid {
              background-color: #dcfce7;
              color: #166534;
            }
            .badge-finalized {
              background-color: #dbeafe;
              color: #0c4a6e;
            }
            .badge-draft {
              background-color: #fef3c7;
              color: #92400e;
            }
            .badge-voided {
              background-color: #fee2e2;
              color: #991b1b;
            }
            .badge-returned {
              background-color: #fce7f3;
              color: #831843;
            }
            .badge-partially_paid {
              background-color: #f3e8ff;
              color: #6b21a8;
            }
            @media print {
              body {
                margin: 0;
              }
              .no-print {
                display: none;
              }
              table {
                page-break-inside: avoid;
              }
            }
          </style>
        </head>
        <body>
          <div class="print-content">
            ${element.innerHTML}
          </div>
          <div class="no-print" style="margin-top: 20px; text-align: center; padding: 20px; color: #6b7280; font-size: 12px;">
            Click <strong>Print</strong> in your browser to print this document.
          </div>
        </body>
      </html>
    `)
    printWindow.document.close()

    // Wait for styles to load before printing
    setTimeout(() => {
      printWindow.print()
    }, 250)
  }

  return {
    printDocument,
  }
}
