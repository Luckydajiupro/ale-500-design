本目录存放本机模型密钥，不得提交。

1. 运行 `tools/wave5/setup_model_secret.sh --from-file /path/to/key`。
2. 或手动创建 `model_api_key`，权限 0600，内容为单行 API Key。
3. `compose.yaml` 以只读 secret 挂载到 `/run/secrets/model_api_key`，容器内 uid 10001 可读。
4. 未配置真实密钥时保持 `ALE_MODEL_PROVIDER=mock`，不得伪造 LIVE_PASS。
