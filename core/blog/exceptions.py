
class PostNotFound(Exception):
    def __init__(self):
        self.detail = 'Blog post not found'
        super().__init__(self.detail)
        
        
class TagNotFound(Exception):
    def __init__(self):
        self.detail = 'Tag not found'
        super().__init__(self.detail)
        
        
class InvalidPostData(Exception):
    
    def __init__(self, message: str, detail=dict):
        self.detail = detail
        super().__init__(message)
        
        
class LikeAlreadyCreated(Exception):
    def __init__(self):
        self.detail = 'User liked this post before'
        super().__init__(self.detail)