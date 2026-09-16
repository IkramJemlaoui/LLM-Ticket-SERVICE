# Internal Application Login Loops

For repeated redirects to an application's login page, capture the application name, browser and version, device, time of the last failed attempt, error or correlation identifier, and whether other company applications work. Safe checks include using the approved sign-out flow, closing the browser, and retrying in a fresh approved session.

Route an application-specific loop to Business Applications. Route a wider password, MFA, or account failure across several services to Identity & Access. Never ask for a password or MFA code.
