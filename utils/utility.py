class Utility:

    @staticmethod
    def split_by_dot(text):
        if not text:
            return[]
        return text.split('.')
    
    @staticmethod
    def get_last_text(text):
        dot_index = text.rfind('.')

        if dot_index == -1:
            return text
        
        return text[dot_index + 1:]