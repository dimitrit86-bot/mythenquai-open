import '../import-core.js';
import './lookup-service.js';
Deno.serve(globalThis.NK_LOOKUP_SERVICE.createHandler({core:globalThis.NK_IMPORT_CORE,base:Deno.env.get('SUPABASE_URL'),service:Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')}));
