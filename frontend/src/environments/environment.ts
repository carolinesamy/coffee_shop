/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-tg3jd163.us', // the auth0 domain prefix
    audience: 'coffe_shop', // the audience set for the auth0 app
    clientId: 'oY4Fz4D6C5c7yroejhpiLn7xne5j2zxs', // the client id generated for the auth0 app
    callbackURL: 'http://127.0.0.1:8100', // the base url of the running ionic application.
  }
};
