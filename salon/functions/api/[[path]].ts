export interface Env {
  BACKEND_URL: string;
}

export const onRequest = async (context: { request: Request; env: Env }) => {
  const backendUrl = context.env.BACKEND_URL || "https://api.kenikoolsalon.com";
  const url = new URL(context.request.url);
  const backendPath = `${backendUrl}${url.pathname}${url.search}`;

  const headers = new Headers(context.request.headers);
  headers.delete("Origin");
  headers.set("X-Forwarded-Host", url.hostname);

  const response = await fetch(backendPath, {
    method: context.request.method,
    headers,
    body: context.request.body,
    redirect: "follow",
  });

  const responseHeaders = new Headers(response.headers);
  responseHeaders.set("Access-Control-Allow-Origin", "*");
  responseHeaders.set("Access-Control-Allow-Methods", "*");
  responseHeaders.set("Access-Control-Allow-Headers", "*");
  responseHeaders.set("Access-Control-Allow-Credentials", "true");

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
};
