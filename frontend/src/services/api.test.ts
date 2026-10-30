import { afterEach, describe, expect, it, vi } from 'vitest';
import { api } from './api';
afterEach(()=>vi.unstubAllGlobals());
describe('Erros de transporte',()=>{
  it('explica indisponibilidade da API em português',async()=>{
    vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
    await expect(api('/health')).rejects.toThrow('A API está indisponível');
  });
  it('preserva a mensagem de validação do servidor',async()=>{
    vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response(JSON.stringify({detail:'Confira os valores: há parâmetros inválidos.'}),{status:422})));
    await expect(api('/simulations/preview','POST',{})).rejects.toThrow('Confira os valores');
  });
});
