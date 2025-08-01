#!/usr/bin/env python3
"""
BaaS SMS/MMS MCP Server

Model Context Protocol server for SMS and MMS messaging services.
This server provides tools for sending SMS/MMS messages, checking message status,
and retrieving sending history through BaaS API integration.
"""

import os
import httpx
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

# Create the FastMCP instance for SMS/MMS messaging service
mcp = FastMCP("baas-mcp")

# Configuration
API_BASE_URL = "https://api.aiapp.link"  # Fixed BaaS API endpoint
BAAS_API_KEY = os.getenv("BAAS_API_KEY", "")

# HTTP client setup
client = httpx.AsyncClient(timeout=30.0)

@mcp.tool()
async def get_code_template_url(
    language: str,
    framework: Optional[str] = None,
    deployment_platform: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get URL for BaaS SMS/MMS integration code template from CDN
    
    Perfect for: Getting optimized, maintained code templates without token overhead
    
    Args:
        language: Programming language (javascript, python, php, java, go, csharp)
        framework: Optional framework (react, vue, django, laravel, fastapi, spring, etc.)
        deployment_platform: Optional platform (vercel, netlify, aws, docker, etc.)
    
    Returns:
        CDN URL to markdown file with complete code examples and integration guide
        Templates include direct API calls to https://api.aiapp.link
    """
    try:
        language = language.lower()
        framework = framework.lower() if framework else None
        platform = deployment_platform.lower() if deployment_platform else None
        
        # CDN base URL with llms.txt optimization
        base_url = "https://cdn.mbaas.kr/templates/sms-mms"
        
        # Construct template path
        template_path = language
        if framework:
            template_path += f"/{framework}"
        else:
            template_path += "/vanilla"
        
        template_url = f"{base_url}/{template_path}.md"
        
        # Platform-specific integration guide
        integration_url = None
        if platform:
            integration_url = f"{base_url}/deployment/{platform}.md"
        
        # Supported combinations
        supported_languages = ["javascript", "python", "php", "java", "go", "csharp"]
        supported_frameworks = {
            "javascript": ["react", "vue", "nextjs", "express", "nodejs"],
            "python": ["django", "fastapi", "flask", "python"],
            "php": ["laravel", "symfony", "php"],
            "java": ["spring", "springboot"],
            "go": ["gin", "echo", "fiber"],
            "csharp": ["aspnet", "dotnet"]
        }
        
        if language not in supported_languages:
            return {
                "success": False,
                "error": f"언어 '{language}'는 아직 지원되지 않습니다",
                "supported_languages": supported_languages,
                "error_code": "UNSUPPORTED_LANGUAGE"
            }
        
        return {
            "success": True,
            "language": language,
            "framework": framework,
            "deployment_platform": platform,
            "template_url": template_url,
            "integration_url": integration_url,
            "api_endpoint": "https://api.aiapp.link",
            "cdn_info": {
                "cache_duration": "24시간",
                "last_updated": "자동 업데이트",
                "version": "latest"
            },
            "configuration": {
                "required_env_vars": ["BAAS_API_KEY", "BAAS_PROJECT_ID"],
                "installation_guide": f"{base_url}/setup/{language}.md"
            },
            "message": f"{language} 템플릿 URL을 제공합니다. 토큰 최적화를 위해 CDN에서 직접 다운로드하세요."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"템플릿 URL 생성에 실패했습니다: {str(e)}",
            "error_code": "URL_GENERATION_ERROR"
        }

@mcp.tool()
async def send_sms(
    recipients: List[Dict[str, str]],
    message: str,
    callback_number: str,
    project_id: str
) -> Dict[str, Any]:
    """
    Send SMS message to one or multiple recipients for user authentication, notifications, or marketing campaigns
    
    Perfect for: user registration verification, order confirmations, 2FA codes, promotional messages
    
    Args:
        recipients: List of recipients with phone_number (Korean format: 010-1234-5678) and member_code (unique identifier)
        message: SMS message content (max 2000 characters, supports Korean text)
        callback_number: Sender callback number (your business number)
        project_id: Project UUID (required)
    
    Returns:
        Dictionary with success status, group_id for tracking, and sending statistics
        Use group_id with get_message_status() to check delivery
    """
    try:
        if not project_id:
            return {
                "success": False,
                "error": "프로젝트 ID가 필요합니다",
                "error_code": "MISSING_PROJECT_ID"
            }
        
        # Validate input
        if not recipients or len(recipients) > 1000:
            return {
                "success": False,
                "error": "수신자 수는 1명 이상 1000명 이하여야 합니다",
                "error_code": "INVALID_RECIPIENTS_COUNT"
            }
        
        if len(message) > 2000:
            return {
                "success": False,
                "error": "메시지 길이가 2000자를 초과했습니다",
                "error_code": "MESSAGE_TOO_LONG"
            }
        
        # Prepare API request
        payload = {
            "recipients": recipients,
            "message": message,
            "callback_number": callback_number,
            "project_id": project_id,
            "channel_id": 1  # SMS channel
        }
        
        headers = {
            "X-API-KEY": f"{BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Make API call
        response = await client.post(
            f"{API_BASE_URL}/message/sms",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return {
                    "success": True,
                    "group_id": result["data"]["group_id"],
                    "message": "SMS가 성공적으로 전송되었습니다",
                    "sent_count": len(recipients),
                    "failed_count": 0
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "error_code": result.get("error_code", "UNKNOWN_ERROR")
                }
        else:
            return {
                "success": False,
                "error": f"API 호출이 실패했습니다 (상태코드: {response.status_code})",
                "error_code": "API_ERROR"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"SMS 전송에 실패했습니다: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

@mcp.tool()
async def send_mms(
    recipients: List[Dict[str, str]],
    message: str,
    subject: str,
    callback_number: str,
    project_id: str,
    image_urls: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Send MMS message with images to one or multiple recipients for rich media marketing and notifications
    
    Perfect for: product catalogs, order confirmations with photos, event invitations, visual promotions
    
    Args:
        recipients: List of recipients with phone_number (Korean format: 010-1234-5678) and member_code (unique identifier)
        message: MMS message content (max 2000 characters, supports Korean text and emojis)
        subject: MMS subject line (max 40 characters, appears as message title)
        callback_number: Sender callback number (your business number)
        project_id: Project UUID (required)
        image_urls: List of publicly accessible image URLs to attach (max 5 images, JPG/PNG format)
        
    Returns:
        Dictionary with success status, group_id for tracking, and sending statistics
        Use group_id with get_message_status() to check delivery and view analytics
    """
    try:
        if not project_id:
            return {
                "success": False,
                "error": "프로젝트 ID가 필요합니다",
                "error_code": "MISSING_PROJECT_ID"
            }
        
        # Validate input
        if not recipients or len(recipients) > 1000:
            return {
                "success": False,
                "error": "수신자 수는 1명 이상 1000명 이하여야 합니다",
                "error_code": "INVALID_RECIPIENTS_COUNT"
            }
        
        if len(message) > 2000:
            return {
                "success": False,
                "error": "메시지 길이가 2000자를 초과했습니다",
                "error_code": "MESSAGE_TOO_LONG"
            }
        
        if len(subject) > 40:
            return {
                "success": False,
                "error": "제목 길이가 40자를 초과했습니다",
                "error_code": "SUBJECT_TOO_LONG"
            }
        
        if image_urls and len(image_urls) > 5:
            return {
                "success": False,
                "error": "최대 5개의 이미지만 첨부 가능합니다",
                "error_code": "TOO_MANY_IMAGES"
            }
        
        # Prepare API request
        payload = {
            "recipients": recipients,
            "message": message,
            "subject": subject,
            "callback_number": callback_number,
            "project_id": project_id,
            "channel_id": 3,  # MMS channel
            "img_url_list": image_urls or []
        }
        
        headers = {
            "X-API-KEY": f"{BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Make API call
        response = await client.post(
            f"{API_BASE_URL}/message/mms",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return {
                    "success": True,
                    "group_id": result["data"]["group_id"],
                    "message": "MMS가 성공적으로 전송되었습니다",
                    "sent_count": len(recipients),
                    "failed_count": 0
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "error_code": result.get("error_code", "UNKNOWN_ERROR")
                }
        else:
            return {
                "success": False,
                "error": f"API 호출이 실패했습니다 (상태코드: {response.status_code})",
                "error_code": "API_ERROR"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"MMS 전송에 실패했습니다: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

@mcp.tool()
async def get_message_status(group_id: int) -> Dict[str, Any]:
    """
    Get detailed message delivery status and analytics by group ID for monitoring and debugging
    
    Perfect for: checking delivery success rates, debugging failed messages, generating delivery reports
    
    Args:
        group_id: Message group ID returned from send_sms() or send_mms() functions
        
    Returns:
        Dictionary with overall delivery status, success/failure counts, and individual recipient details
        Status values: "전송중" (sending), "성공" (success), "실패" (failed), "부분성공" (partial success)
    """
    try:
        headers = {
            "X-API-KEY": f"{BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Make API call to get message status
        response = await client.get(
            f"{API_BASE_URL}/message/send_history/sms/{group_id}/messages",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                messages = result.get("data", [])
                
                # Calculate statistics
                total_count = len(messages)
                success_count = sum(1 for msg in messages if msg.get("result") == "성공")
                failed_count = sum(1 for msg in messages if msg.get("result") == "실패")
                pending_count = total_count - success_count - failed_count
                
                # Determine overall status
                if pending_count > 0:
                    status = "전송중"
                elif failed_count == 0:
                    status = "성공"
                else:
                    status = "실패" if success_count == 0 else "부분성공"
                
                return {
                    "group_id": group_id,
                    "status": status,
                    "total_count": total_count,
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "pending_count": pending_count,
                    "messages": [
                        {
                            "phone": msg.get("phone", ""),
                            "name": msg.get("name", ""),
                            "status": msg.get("result", ""),
                            "reason": msg.get("reason")
                        }
                        for msg in messages
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "메시지 상태 조회에 실패했습니다"),
                    "error_code": result.get("error_code", "UNKNOWN_ERROR")
                }
        else:
            return {
                "success": False,
                "error": f"API 호출이 실패했습니다 (상태코드: {response.status_code})",
                "error_code": "API_ERROR"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"메시지 상태 조회에 실패했습니다: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

@mcp.tool()
async def get_send_history(
    project_id: str,
    offset: int = 0,
    limit: int = 20,
    message_type: str = "ALL"
) -> Dict[str, Any]:
    """
    Get message sending history for a project
    
    Args:
        project_id: Project UUID (required)
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 20, max: 100)
        message_type: Filter by message type ("SMS", "MMS", "ALL")
        
    Returns:
        Dictionary with sending history data
    """
    try:
        if not project_id:
            return {
                "success": False,
                "error": "프로젝트 ID가 필요합니다",
                "error_code": "MISSING_PROJECT_ID"
            }
        
        # Validate parameters
        if limit > 100:
            limit = 100
        if offset < 0:
            offset = 0
        if message_type not in ["SMS", "MMS", "ALL"]:
            message_type = "ALL"
        
        headers = {
            "X-API-KEY": f"{BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        params = {
            "offset": offset,
            "limit": limit,
            "message_type": message_type
        }
        
        # Make API call (Note: This endpoint needs to be implemented in the API)
        # For now, return a placeholder response
        return {
            "success": True,
            "data": {
                "project_id": project_id,
                "total_count": 0,
                "offset": offset,
                "limit": limit,
                "message_type": message_type,
                "history": []
            },
            "message": "전송 기록 엔드포인트가 아직 API에 구현되지 않았습니다"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"전송 기록 조회에 실패했습니다: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

@mcp.tool()
async def generate_direct_api_code(
    language: str = "javascript",
    framework: Optional[str] = None,
    include_examples: bool = True
) -> Dict[str, Any]:
    """
    Generate code that directly calls BaaS API by fetching templates from CDN
    
    Perfect for: Production deployments, custom integrations, framework-specific implementations
    Token-optimized: Fetches maintained templates from CDN instead of generating locally
    
    Args:
        language: Programming language (javascript, python, php, java, go, csharp)
        framework: Optional framework (react, vue, django, laravel, fastapi, spring, etc.)
        include_examples: Include usage examples and configuration templates
        
    Returns:
        Dictionary with code fetched from CDN, filename, and integration instructions
        Code directly calls https://api.aiapp.link with proper authentication
    """
    try:
        language = language.lower()
        framework = framework.lower() if framework else None
        
        # CDN base URL for templates
        base_url = "https://cdn.baas-templates.com/sms-mms"
        
        # Construct template path
        template_path = language
        if framework:
            template_path += f"/{framework}"
        else:
            template_path += "/vanilla"
        
        template_url = f"{base_url}/{template_path}.md"
        
        # Fetch template from CDN
        try:
            response = await client.get(template_url)
            if response.status_code == 200:
                template_content = response.text
                
                # Extract code from markdown (assuming code is in ```language blocks)
                import re
                code_blocks = re.findall(f'```{language}(.*?)```', template_content, re.DOTALL)
                
                if code_blocks:
                    code = code_blocks[0].strip()
                else:
                    # Fallback: use entire content if no code blocks found
                    code = template_content
                    
            else:
                # Fallback to local generation if CDN is unavailable
                if language == "javascript" or language == "js":
                    code = generate_javascript_code(framework, include_examples)
                elif language == "python" or language == "py":
                    code = generate_python_code(framework, include_examples)
                elif language == "php":
                    code = generate_php_code(framework, include_examples)
                else:
                    return {
                        "success": False,
                        "error": f"CDN에서 템플릿을 가져올 수 없고, 언어 '{language}'는 로컬 생성을 지원하지 않습니다",
                        "supported_languages": ["javascript", "python", "php"],
                        "error_code": "TEMPLATE_UNAVAILABLE"
                    }
                    
        except Exception as cdn_error:
            # Fallback to local generation
            if language == "javascript" or language == "js":
                code = generate_javascript_code(framework, include_examples)
            elif language == "python" or language == "py":
                code = generate_python_code(framework, include_examples)
            elif language == "php":
                code = generate_php_code(framework, include_examples)
            else:
                return {
                    "success": False,
                    "error": f"CDN 오류 및 로컬 생성 불가: {str(cdn_error)}",
                    "error_code": "GENERATION_FAILED"
                }
        
        # File naming
        extensions = {
            "javascript": "js",
            "js": "js", 
            "python": "py",
            "py": "py",
            "php": "php"
        }
        
        extension = extensions.get(language, language)
        filename = f"baas-sms-service.{extension}"
        
        # Configuration instructions
        config_instructions = {
            "javascript": {
                "env_vars": ["BAAS_API_KEY", "BAAS_PROJECT_ID"],
                "install": "npm install (dependencies included in template)",
                "usage": "Import and instantiate BaaSMessageService class"
            },
            "python": {
                "env_vars": ["BAAS_API_KEY", "BAAS_PROJECT_ID"],
                "install": "pip install requests",
                "usage": "Import and instantiate BaaSMessageService class"
            },
            "php": {
                "env_vars": ["BAAS_API_KEY", "BAAS_PROJECT_ID"],
                "install": "cURL extension required (usually included)",
                "usage": "Include file and instantiate BaaSMessageService class"
            }
        }
        
        return {
            "success": True,
            "language": language,
            "framework": framework,
            "code": code,
            "filename": filename,
            "description": f"{language.title()} BaaS SMS service for direct API calls",
            "source": "CDN template" if 'template_content' in locals() else "Local generation",
            "template_url": template_url,
            "configuration": config_instructions.get(language, {}),
            "api_endpoint": "https://api.aiapp.link",
            "message": f"{language.title()} 코드가 성공적으로 생성되었습니다 (소스: {'CDN' if 'template_content' in locals() else '로컬'})"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"코드 생성에 실패했습니다: {str(e)}",
            "error_code": "CODE_GENERATION_ERROR"
        }

@mcp.tool()
async def create_message_service_template(
    project_config: Dict[str, str],
    language: str = "javascript",
    features: List[str] = None
) -> Dict[str, Any]:
    """
    Create a complete message service template by fetching from CDN and customizing with project config
    
    Perfect for: New project setup, team standardization, rapid prototyping
    Token-optimized: Fetches base template from CDN then applies project customizations
    
    Args:
        project_config: Project configuration {project_id, default_callback, company_name, etc.}
        language: Target programming language
        features: List of features to include ["sms", "mms", "status_check", "history", "validation"]
        
    Returns:
        Complete service template with project-specific defaults and configuration
    """
    try:
        if features is None:
            features = ["sms", "mms", "status_check"]
        
        # Extract project configuration
        project_id = project_config.get("project_id", "your-project-id")
        default_callback = project_config.get("default_callback", "02-1234-5678")
        company_name = project_config.get("company_name", "Your Company")
        
        # Fetch base template from CDN
        base_result = await generate_direct_api_code(language, None, True)
        
        if not base_result.get("success"):
            return base_result
        
        # Customize code with project config
        code = base_result["code"]
        
        # Replace placeholders with actual project values
        code = code.replace("your-project-id", project_id)
        code = code.replace("02-1234-5678", default_callback)
        code = code.replace("Your Company", company_name)
        
        # Fetch project-specific helpers from CDN
        try:
            helpers_url = f"https://cdn.baas-templates.com/sms-mms/helpers/{language}-project.md"
            response = await client.get(helpers_url)
            
            if response.status_code == 200:
                helpers_template = response.text
                
                # Replace placeholders in helpers template
                helpers_code = helpers_template.replace("{{company_name}}", company_name)
                helpers_code = helpers_code.replace("{{project_id}}", project_id)
                helpers_code = helpers_code.replace("{{default_callback}}", default_callback)
                
                code += "\n\n" + helpers_code
                
        except Exception:
            # Fallback to basic project helpers if CDN unavailable
            if language == "javascript":
                project_helpers = f'''
// {company_name} Project-Specific Helpers
const PROJECT_CONFIG = {{
    PROJECT_ID: '{project_id}',
    DEFAULT_CALLBACK: '{default_callback}',
    COMPANY_NAME: '{company_name}'
}};

// Pre-configured service instance
const messageService = new BaaSMessageService(
    process.env.BAAS_API_KEY || 'your-api-key',
    PROJECT_CONFIG.PROJECT_ID
);

// Helper functions for common use cases
async function sendVerificationSMS(phoneNumber, code, memberCode) {{
    return await messageService.sendSMS(
        [{{ phone_number: phoneNumber, member_code: memberCode }}],
        `[{company_name}] 인증번호: ${{code}}`,
        PROJECT_CONFIG.DEFAULT_CALLBACK
    );
}}

async function sendOrderConfirmation(phoneNumber, orderNumber, memberCode) {{
    return await messageService.sendSMS(
        [{{ phone_number: phoneNumber, member_code: memberCode }}],
        `[{company_name}] 주문이 완료되었습니다. 주문번호: ${{orderNumber}}`,
        PROJECT_CONFIG.DEFAULT_CALLBACK
    );
}}'''
                code += project_helpers
        
        return {
            "success": True,
            "project_config": project_config,
            "language": language,
            "features": features,
            "code": code,
            "filename": f"{company_name.lower().replace(' ', '_')}_message_service.{language}",
            "description": f"{company_name} 전용 메시지 서비스 템플릿",
            "source": "CDN template + project customization",
            "message": "프로젝트별 맞춤 코드가 생성되었습니다 (CDN 최적화)"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"템플릿 생성에 실패했습니다: {str(e)}",
            "error_code": "TEMPLATE_GENERATION_ERROR"
        }

@mcp.tool()
async def get_integration_guide(
    platform: str,
    deployment_type: str = "production"
) -> Dict[str, Any]:
    """
    Get detailed integration guide by fetching from CDN for specific platforms and deployment scenarios
    
    Perfect for: DevOps setup, deployment planning, team onboarding
    Token-optimized: Fetches comprehensive guides from CDN instead of hardcoded responses
    
    Args:
        platform: Target platform (vercel, netlify, heroku, aws, gcp, azure, docker, etc.)
        deployment_type: Deployment type (development, staging, production)
        
    Returns:
        Step-by-step integration guide with platform-specific instructions fetched from CDN
    """
    try:
        platform = platform.lower()
        deployment_type = deployment_type.lower()
        
        # Try to fetch guide from CDN
        guide_url = f"https://cdn.baas-templates.com/sms-mms/deployment/{platform}-{deployment_type}.md"
        
        try:
            response = await client.get(guide_url)
            if response.status_code == 200:
                guide_content = response.text
                
                return {
                    "success": True,
                    "platform": platform,
                    "deployment_type": deployment_type,
                    "guide_content": guide_content,
                    "source": "CDN",
                    "guide_url": guide_url,
                    "security_checklist": [
                        "API 키를 코드에 하드코딩하지 않기",
                        "환경 변수 또는 시크릿 관리 서비스 사용",
                        "HTTPS 통신 확인",
                        "적절한 에러 로깅 설정"
                    ],
                    "message": f"{platform.title()} {deployment_type} 배포 가이드입니다 (CDN 최적화)"
                }
        except Exception:
            # Fallback to basic guides if CDN unavailable
            pass
        
        # Fallback guides
        basic_guides = {
            "vercel": {
                "title": "Vercel 배포 가이드",
                "steps": [
                    "1. 환경 변수 설정: BAAS_API_KEY, BAAS_PROJECT_ID",
                    "2. vercel.json 설정에 환경 변수 추가",
                    "3. API Routes에서 BaaSMessageService 사용",
                    "4. Edge Runtime 호환성 확인"
                ],
                "config": {
                    "env_vars": "Vercel Dashboard > Settings > Environment Variables",
                    "api_routes": "/api/send-sms.js 형태로 구현",
                    "limitations": "Edge Runtime에서는 Node.js APIs 제한"
                }
            },
            "netlify": {
                "title": "Netlify Functions 가이드",
                "steps": [
                    "1. netlify/functions 디렉토리에 함수 생성",
                    "2. 환경 변수를 Netlify 대시보드에서 설정",
                    "3. BaaSMessageService를 Serverless Function에서 사용",
                    "4. 빌드 설정에 필요한 패키지 의존성 추가"
                ]
            },
            "docker": {
                "title": "Docker 컨테이너 배포",
                "steps": [
                    "1. Dockerfile에 필요한 의존성 설치",
                    "2. ENV 명령어로 환경 변수 설정",
                    "3. 또는 docker run -e 옵션 사용",
                    "4. 네트워크 접근성 확인 (api.aiapp.link)"
                ]
            }
        }
        
        guide = basic_guides.get(platform)
        
        if not guide:
            return {
                "success": False,
                "error": f"플랫폼 '{platform}'에 대한 가이드가 아직 준비되지 않았습니다",
                "available_platforms": list(basic_guides.keys()),
                "cdn_url": f"https://cdn.baas-templates.com/sms-mms/deployment/",
                "error_code": "PLATFORM_NOT_SUPPORTED"
            }
        
        # Add deployment-specific notes
        deployment_notes = {
            "development": "개발 환경에서는 .env 파일 사용 권장",
            "staging": "스테이징 환경에서는 별도 프로젝트 ID 사용",
            "production": "프로덕션에서는 환경 변수 암호화 및 로깅 설정 필요"
        }
        
        return {
            "success": True,
            "platform": platform,
            "deployment_type": deployment_type,
            "guide": guide,
            "source": "Local fallback",
            "deployment_notes": deployment_notes.get(deployment_type, ""),
            "security_checklist": [
                "API 키를 코드에 하드코딩하지 않기",
                "환경 변수 또는 시크릿 관리 서비스 사용",
                "HTTPS 통신 확인",
                "적절한 에러 로깅 설정"
            ],
            "message": f"{platform.title()} {deployment_type} 배포 가이드입니다 (로컬 폴백)"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"가이드 조회에 실패했습니다: {str(e)}",
            "error_code": "GUIDE_RETRIEVAL_ERROR"
        }

# Code generation functions
def generate_javascript_code(framework: Optional[str] = None, include_examples: bool = True) -> str:
    """Generate JavaScript code for direct BaaS API calls"""
    
    base_code = '''/**
 * BaaS SMS/MMS Direct API Client
 * Directly calls https://api.aiapp.link without MCP
 */

class BaaSMessageService {
    constructor(apiKey, projectId, baseUrl = 'https://api.aiapp.link') {
        this.apiKey = apiKey;
        this.projectId = projectId;
        this.baseUrl = baseUrl;
    }
    
    /**
     * Send SMS message
     * @param {Array} recipients - Array of {phone_number, member_code}
     * @param {string} message - Message content (max 2000 chars)
     * @param {string} callbackNumber - Sender callback number
     * @returns {Promise<Object>} Response object
     */
    async sendSMS(recipients, message, callbackNumber) {
        try {
            const response = await fetch(`${this.baseUrl}/message/sms`, {
                method: 'POST',
                headers: {
                    'X-API-KEY': this.apiKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipients: recipients,
                    message: message,
                    callback_number: callbackNumber,
                    project_id: this.projectId,
                    channel_id: 1
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                return {
                    success: true,
                    groupId: result.data.group_id,
                    message: 'SMS sent successfully'
                };
            } else {
                return {
                    success: false,
                    error: result.message || 'Send failed',
                    errorCode: result.error_code
                };
            }
        } catch (error) {
            return {
                success: false,
                error: `Network error: ${error.message}`
            };
        }
    }
    
    /**
     * Send MMS message with images
     * @param {Array} recipients - Array of {phone_number, member_code}
     * @param {string} message - Message content
     * @param {string} subject - MMS subject (max 40 chars)
     * @param {string} callbackNumber - Sender callback number
     * @param {Array} imageUrls - Array of image URLs (max 5)
     * @returns {Promise<Object>} Response object
     */
    async sendMMS(recipients, message, subject, callbackNumber, imageUrls = []) {
        try {
            const response = await fetch(`${this.baseUrl}/message/mms`, {
                method: 'POST',
                headers: {
                    'X-API-KEY': this.apiKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipients: recipients,
                    message: message,
                    subject: subject,
                    callback_number: callbackNumber,
                    project_id: this.projectId,
                    channel_id: 3,
                    img_url_list: imageUrls
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                return {
                    success: true,
                    groupId: result.data.group_id,
                    message: 'MMS sent successfully'
                };
            } else {
                return {
                    success: false,
                    error: result.message || 'Send failed',
                    errorCode: result.error_code
                };
            }
        } catch (error) {
            return {
                success: false,
                error: `Network error: ${error.message}`
            };
        }
    }
    
    /**
     * Check message delivery status
     * @param {number} groupId - Message group ID
     * @returns {Promise<Object>} Status information
     */
    async getMessageStatus(groupId) {
        try {
            const response = await fetch(
                `${this.baseUrl}/message/send_history/sms/${groupId}/messages`,
                {
                    method: 'GET',
                    headers: {
                        'X-API-KEY': this.apiKey,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                const messages = result.data || [];
                const totalCount = messages.length;
                const successCount = messages.filter(msg => msg.result === '성공').length;
                const failedCount = messages.filter(msg => msg.result === '실패').length;
                const pendingCount = totalCount - successCount - failedCount;
                
                let status = '전송중';
                if (pendingCount === 0) {
                    status = failedCount === 0 ? '성공' : 
                            (successCount === 0 ? '실패' : '부분성공');
                }
                
                return {
                    groupId: groupId,
                    status: status,
                    totalCount: totalCount,
                    successCount: successCount,
                    failedCount: failedCount,
                    pendingCount: pendingCount,
                    messages: messages.map(msg => ({
                        phone: msg.phone,
                        name: msg.name,
                        status: msg.result,
                        reason: msg.reason
                    }))
                };
            } else {
                return {
                    success: false,
                    error: result.message || 'Status check failed'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: `Network error: ${error.message}`
            };
        }
    }
}'''

    # Framework-specific additions
    if framework == 'react':
        base_code += '''

/**
 * React Hook for BaaS SMS service
 */
import { useState, useCallback } from 'react';

export function useBaaSMessageService(apiKey, projectId) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const service = new BaaSMessageService(apiKey, projectId);
    
    const sendSMS = useCallback(async (recipients, message, callbackNumber) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await service.sendSMS(recipients, message, callbackNumber);
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [service]);
    
    const sendMMS = useCallback(async (recipients, message, subject, callbackNumber, imageUrls) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await service.sendMMS(recipients, message, subject, callbackNumber, imageUrls);
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [service]);
    
    return {
        sendSMS,
        sendMMS,
        getMessageStatus: service.getMessageStatus.bind(service),
        loading,
        error
    };
}'''
    
    elif framework == 'vue':
        base_code += '''

/**
 * Vue 3 Composition API for BaaS SMS service
 */
import { ref, reactive } from 'vue';

export function useBaaSMessageService(apiKey, projectId) {
    const loading = ref(false);
    const error = ref(null);
    
    const service = new BaaSMessageService(apiKey, projectId);
    
    const sendSMS = async (recipients, message, callbackNumber) => {
        loading.value = true;
        error.value = null;
        
        try {
            const result = await service.sendSMS(recipients, message, callbackNumber);
            return result;
        } catch (err) {
            error.value = err.message;
            throw err;
        } finally {
            loading.value = false;
        }
    };
    
    const sendMMS = async (recipients, message, subject, callbackNumber, imageUrls) => {
        loading.value = true;
        error.value = null;
        
        try {
            const result = await service.sendMMS(recipients, message, subject, callbackNumber, imageUrls);
            return result;
        } catch (err) {
            error.value = err.message;
            throw err;
        } finally {
            loading.value = false;
        }
    };
    
    return {
        sendSMS,
        sendMMS,
        getMessageStatus: service.getMessageStatus.bind(service),
        loading,
        error
    };
}'''

    # Add usage examples
    if include_examples:
        base_code += '''

// Usage Examples

// Example 1: Basic SMS sending
const messageService = new BaaSMessageService('your-api-key', 'your-project-id');

const recipients = [
    { phone_number: "010-1234-5678", member_code: "user_001" }
];

// Send SMS
messageService.sendSMS(
    recipients,
    "안녕하세요! 인증번호는 123456입니다.",
    "02-1234-5678"
).then(result => {
    console.log('SMS Result:', result);
    if (result.success) {
        // Check status
        return messageService.getMessageStatus(result.groupId);
    }
}).then(status => {
    console.log('Status:', status);
});

// Example 2: MMS with images
messageService.sendMMS(
    recipients,
    "신상품 출시 안내드립니다!",
    "신상품 알림",
    "02-1234-5678",
    ["https://example.com/product.jpg"]
).then(result => {
    console.log('MMS Result:', result);
});

// Example 3: Environment-based configuration
const apiKey = process.env.BAAS_API_KEY || 'your-api-key';
const projectId = process.env.BAAS_PROJECT_ID || 'your-project-id';
const service = new BaaSMessageService(apiKey, projectId);'''

    # Node.js export
    base_code += '''

// Node.js export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BaaSMessageService };
}

// ES6 export
export { BaaSMessageService };'''

    return base_code

def generate_python_code(framework: Optional[str] = None, include_examples: bool = True) -> str:
    """Generate Python code for direct BaaS API calls"""
    
    base_code = '''"""
BaaS SMS/MMS Direct API Client
Directly calls https://api.aiapp.link without MCP
"""

import requests
import json
from typing import List, Dict, Optional, Union

class BaaSMessageService:
    def __init__(self, api_key: str, project_id: str, base_url: str = 'https://api.aiapp.link'):
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = base_url
        
    def send_sms(self, recipients: List[Dict], message: str, callback_number: str) -> Dict:
        """
        Send SMS message
        
        Args:
            recipients: List of {phone_number, member_code}
            message: Message content (max 2000 chars)
            callback_number: Sender callback number
            
        Returns:
            Dict: Response object
        """
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'recipients': recipients,
                'message': message,
                'callback_number': callback_number,
                'project_id': self.project_id,
                'channel_id': 1
            }
            
            response = requests.post(
                f'{self.base_url}/message/sms',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                return {
                    'success': True,
                    'group_id': result['data']['group_id'],
                    'message': 'SMS sent successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Send failed'),
                    'error_code': result.get('error_code')
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def send_mms(self, recipients: List[Dict], message: str, subject: str, 
                callback_number: str, image_urls: Optional[List[str]] = None) -> Dict:
        """
        Send MMS message with images
        
        Args:
            recipients: List of {phone_number, member_code}
            message: Message content
            subject: MMS subject (max 40 chars)
            callback_number: Sender callback number
            image_urls: List of image URLs (max 5)
            
        Returns:
            Dict: Response object
        """
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'recipients': recipients,
                'message': message,
                'subject': subject,
                'callback_number': callback_number,
                'project_id': self.project_id,
                'channel_id': 3,
                'img_url_list': image_urls or []
            }
            
            response = requests.post(
                f'{self.base_url}/message/mms',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                return {
                    'success': True,
                    'group_id': result['data']['group_id'],
                    'message': 'MMS sent successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Send failed'),
                    'error_code': result.get('error_code')
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def get_message_status(self, group_id: int) -> Dict:
        """
        Check message delivery status
        
        Args:
            group_id: Message group ID
            
        Returns:
            Dict: Status information
        """
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{self.base_url}/message/send_history/sms/{group_id}/messages',
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                messages = result.get('data', [])
                total_count = len(messages)
                success_count = sum(1 for msg in messages if msg.get('result') == '성공')
                failed_count = sum(1 for msg in messages if msg.get('result') == '실패')
                pending_count = total_count - success_count - failed_count
                
                if pending_count > 0:
                    status = '전송중'
                elif failed_count == 0:
                    status = '성공'
                else:
                    status = '실패' if success_count == 0 else '부분성공'
                
                return {
                    'group_id': group_id,
                    'status': status,
                    'total_count': total_count,
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'pending_count': pending_count,
                    'messages': [
                        {
                            'phone': msg.get('phone', ''),
                            'name': msg.get('name', ''),
                            'status': msg.get('result', ''),
                            'reason': msg.get('reason')
                        }
                        for msg in messages
                    ]
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Status check failed')
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }'''

    # Framework-specific additions
    if framework == 'django':
        base_code += '''

# Django integration
from django.conf import settings
from django.core.cache import cache

class DjangoBaaSMessageService(BaaSMessageService):
    def __init__(self, project_id: str = None):
        api_key = getattr(settings, 'BAAS_API_KEY', None)
        project_id = project_id or getattr(settings, 'BAAS_PROJECT_ID', None)
        
        if not api_key:
            raise ValueError("BAAS_API_KEY must be set in Django settings")
        if not project_id:
            raise ValueError("BAAS_PROJECT_ID must be provided or set in Django settings")
            
        super().__init__(api_key, project_id)
    
    def send_sms_cached(self, recipients: List[Dict], message: str, callback_number: str, cache_timeout: int = 300) -> Dict:
        """Send SMS with caching for duplicate prevention"""
        cache_key = f"baas_sms_{hash(str(recipients))}{hash(message)}"
        
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        result = self.send_sms(recipients, message, callback_number)
        
        if result.get('success'):
            cache.set(cache_key, result, cache_timeout)
            
        return result'''

    elif framework == 'fastapi':
        base_code += '''

# FastAPI integration
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from typing import List

class SMSRequest(BaseModel):
    recipients: List[Dict[str, str]]
    message: str
    callback_number: str

class MMSRequest(BaseModel):
    recipients: List[Dict[str, str]]
    message: str
    subject: str
    callback_number: str
    image_urls: Optional[List[str]] = []

def get_baas_service():
    """FastAPI dependency for BaaS service"""
    import os
    api_key = os.getenv('BAAS_API_KEY')
    project_id = os.getenv('BAAS_PROJECT_ID')
    
    if not api_key or not project_id:
        raise HTTPException(status_code=500, detail="BaaS configuration missing")
        
    return BaaSMessageService(api_key, project_id)

# FastAPI route examples
async def send_sms_endpoint(request: SMSRequest, service: BaaSMessageService = Depends(get_baas_service)):
    result = service.send_sms(request.recipients, request.message, request.callback_number)
    
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('error'))
        
    return result'''

    # Add usage examples
    if include_examples:
        base_code += '''

# Usage Examples
if __name__ == "__main__":
    import os
    
    # Configuration from environment variables
    api_key = os.getenv('BAAS_API_KEY', 'your-api-key')
    project_id = os.getenv('BAAS_PROJECT_ID', 'your-project-id')
    
    # Create service instance
    service = BaaSMessageService(api_key, project_id)
    
    # Example 1: Send SMS
    recipients = [
        {"phone_number": "010-1234-5678", "member_code": "user_001"}
    ]
    
    sms_result = service.send_sms(
        recipients,
        "안녕하세요! 인증번호는 123456입니다.",
        "02-1234-5678"
    )
    print("SMS Result:", sms_result)
    
    # Example 2: Send MMS
    if sms_result.get('success'):
        mms_result = service.send_mms(
            recipients,
            "이미지가 포함된 MMS입니다.",
            "MMS 테스트",
            "02-1234-5678",
            ["https://example.com/image.jpg"]
        )
        print("MMS Result:", mms_result)
        
        # Example 3: Check status
        if mms_result.get('success'):
            status = service.get_message_status(mms_result['group_id'])
            print("Message Status:", status)'''

    return base_code

def generate_php_code(framework: Optional[str] = None, include_examples: bool = True) -> str:
    """Generate PHP code for direct BaaS API calls"""
    
    base_code = '''<?php
/**
 * BaaS SMS/MMS Direct API Client
 * Directly calls https://api.aiapp.link without MCP
 */

class BaaSMessageService {
    private $apiKey;
    private $projectId;
    private $baseUrl;
    
    public function __construct($apiKey, $projectId, $baseUrl = 'https://api.aiapp.link') {
        $this->apiKey = $apiKey;
        $this->projectId = $projectId;
        $this->baseUrl = $baseUrl;
    }
    
    /**
     * Send SMS message
     * @param array $recipients Array of ['phone_number' => '', 'member_code' => '']
     * @param string $message Message content (max 2000 chars)
     * @param string $callbackNumber Sender callback number
     * @return array Response array
     */
    public function sendSMS($recipients, $message, $callbackNumber) {
        $payload = [
            'recipients' => $recipients,
            'message' => $message,
            'callback_number' => $callbackNumber,
            'project_id' => $this->projectId,
            'channel_id' => 1
        ];
        
        return $this->makeRequest('/message/sms', $payload);
    }
    
    /**
     * Send MMS message with images
     * @param array $recipients Array of recipients
     * @param string $message Message content
     * @param string $subject MMS subject (max 40 chars)
     * @param string $callbackNumber Sender callback number
     * @param array $imageUrls Array of image URLs (max 5)
     * @return array Response array
     */
    public function sendMMS($recipients, $message, $subject, $callbackNumber, $imageUrls = []) {
        $payload = [
            'recipients' => $recipients,
            'message' => $message,
            'subject' => $subject,
            'callback_number' => $callbackNumber,
            'project_id' => $this->projectId,
            'channel_id' => 3,
            'img_url_list' => $imageUrls
        ];
        
        return $this->makeRequest('/message/mms', $payload);
    }
    
    /**
     * Check message delivery status
     * @param int $groupId Message group ID
     * @return array Status information
     */
    public function getMessageStatus($groupId) {
        $url = "/message/send_history/sms/{$groupId}/messages";
        return $this->makeRequest($url, null, 'GET');
    }
    
    /**
     * Make HTTP request to BaaS API
     * @param string $endpoint API endpoint
     * @param array|null $payload Request payload
     * @param string $method HTTP method
     * @return array Response array
     */
    private function makeRequest($endpoint, $payload = null, $method = 'POST') {
        $headers = [
            'X-API-KEY: ' . $this->apiKey,
            'Content-Type: application/json'
        ];
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $this->baseUrl . $endpoint);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            if ($payload) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
            }
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($response === false || !empty($error)) {
            return [
                'success' => false,
                'error' => 'cURL error: ' . $error
            ];
        }
        
        $result = json_decode($response, true);
        
        if ($httpCode === 200 && isset($result['success']) && $result['success']) {
            return [
                'success' => true,
                'group_id' => $result['data']['group_id'] ?? null,
                'message' => 'Request successful'
            ];
        } else {
            return [
                'success' => false,
                'error' => $result['message'] ?? 'Request failed',
                'error_code' => $result['error_code'] ?? null
            ];
        }
    }
}'''

    # Framework-specific additions
    if framework == 'laravel':
        base_code += '''

/**
 * Laravel Service Provider integration
 */
namespace App\\Services;

use Illuminate\\Support\\Facades\\Config;
use Illuminate\\Support\\Facades\\Cache;

class LaravelBaaSMessageService extends BaaSMessageService {
    public function __construct($projectId = null) {
        $apiKey = Config::get('services.baas.api_key');
        $projectId = $projectId ?: Config::get('services.baas.project_id');
        
        if (!$apiKey || !$projectId) {
            throw new \\Exception('BaaS configuration missing in config/services.php');
        }
        
        parent::__construct($apiKey, $projectId);
    }
    
    /**
     * Send SMS with Laravel caching
     */
    public function sendSMSCached($recipients, $message, $callbackNumber, $cacheMinutes = 5) {
        $cacheKey = 'baas_sms_' . md5(serialize($recipients) . $message);
        
        return Cache::remember($cacheKey, $cacheMinutes, function() use ($recipients, $message, $callbackNumber) {
            return $this->sendSMS($recipients, $message, $callbackNumber);
        });
    }
}

// Add to config/services.php:
/*
'baas' => [
    'api_key' => env('BAAS_API_KEY'),
    'project_id' => env('BAAS_PROJECT_ID'),
],
*/'''

    # Add usage examples
    if include_examples:
        base_code += '''

// Usage Examples

// Basic usage
$apiKey = $_ENV['BAAS_API_KEY'] ?? 'your-api-key';
$projectId = $_ENV['BAAS_PROJECT_ID'] ?? 'your-project-id';

$service = new BaaSMessageService($apiKey, $projectId);

// Example 1: Send SMS
$recipients = [
    ['phone_number' => '010-1234-5678', 'member_code' => 'user_001']
];

$smsResult = $service->sendSMS(
    $recipients,
    '안녕하세요! 인증번호는 123456입니다.',
    '02-1234-5678'
);

echo "SMS Result: " . json_encode($smsResult) . "\\n";

// Example 2: Send MMS
if ($smsResult['success']) {
    $mmsResult = $service->sendMMS(
        $recipients,
        '이미지가 포함된 MMS입니다.',
        'MMS 테스트',
        '02-1234-5678',
        ['https://example.com/image.jpg']
    );
    
    echo "MMS Result: " . json_encode($mmsResult) . "\\n";
    
    // Example 3: Check status
    if ($mmsResult['success'] && isset($mmsResult['group_id'])) {
        $status = $service->getMessageStatus($mmsResult['group_id']);
        echo "Status: " . json_encode($status) . "\\n";
    }
}

?>'''

    return base_code

# Cleanup function to close HTTP client
async def cleanup():
    await client.aclose()

def main():
    """BaaS SMS/MCP 서버의 메인 진입점"""
    print("BaaS SMS/MMS MCP 서버를 시작합니다...")
    print(f"API 기본 URL: {API_BASE_URL}")
    print(f"API 키: {'설정됨' if BAAS_API_KEY else '설정되지 않음'}")
    
    try:
        mcp.run(transport="stdio")
    finally:
        import asyncio
        asyncio.run(cleanup())

# Run the server if the script is executed directly
if __name__ == "__main__":
    main()