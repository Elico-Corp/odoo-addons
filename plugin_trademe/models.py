# -*-coding:utf-8-*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import osv, fields
from openerp import tools
from openerp.tools.translate import _
import logging
import sys
import threading
from TrademeAPI import fetch_all_unanswered_questions, fetch_member_id, fetch_members_listing, reply_to_question,fetch_member_id_and_nick;


_logger = logging.getLogger(__name__)
BASE_URL = "https://api.trademe.co.nz/";
UI_BASE_URL = "http://trademe.co.nz/";

def _get_url(base_url, test=False):
	if test:
		return base_url.replace("trademe.", "tmsandbox.")
	return base_url

class TMMembers(osv.osv):
	def _get_concate(self, cr, uid, ids, field_name, arg, context=None):
			records=self.browse(cr,uid,ids)
			result={}
			for r in records:
				mid = r.member_id if r.member_id else ""
				result[r.id]= _get_url(UI_BASE_URL, r.test)+'Members/Listings.aspx?member='+str(mid)
			return result
	_name = 'tmerp.members'
	_columns = {
		'name': fields.char('Nick Name', required=False, size=100),
		'member_id': fields.char('Member Id', required=False, size=100),
		'consumer_key': fields.char('Consumer Key', required=True, size=50),
		'consumer_secret': fields.char('Consumer Secret', required=True, size=50),
		'access_key': fields.char('Access Key', required=True, size=50),
		'access_secret': fields.char('Access Secret', required=True, size=50),
		'member_url': fields.function(_get_concate, method=True, string='URL', type='char'),
		'is_enabled': fields.boolean('Active'),
		'test': fields.boolean('Sandbox Account'),
	}
	
	_defaults = {
        'test': False,
        'is_enabled': True,
    }
	
	def create(self, cr, uid, vals, context=None):
		member = vals
		try:
			member_id = 0
			member_id, nick = fetch_member_id_and_nick(_get_url(BASE_URL, member.get("test")), member.get("consumer_key"),member.get("consumer_secret"),member.get("access_key"),member.get("access_secret"))
			vals["member_id"] = member_id;
			vals["name"] = nick;
			vals["is_enabled"] = True
		except Exception as ex:
			raise osv.except_osv(_('Unable to connect to the Trademe. Probably invalid keys.'), _(ex.message))
		res = super(TMMembers, self).create(cr, uid, vals, context=context)
		return res;

	def write(self, cr, uid, ids, vals, context=None):
		member = vals
		list = self.pool.get('tmerp.members').browse(cr, uid, ids)
		if len(list) > 0: 
			question = list[0];
		try:
			if vals.get("is_enabled"):
				consumer_key = vals.get("consumer_key") if vals.get("consumer_key") else question.consumer_key 
				consumer_secret= vals.get("consumer_secret") if vals.get("consumer_secret") else question.consumer_secret
				access_key = vals.get("access_key") if vals.get("access_key") else question.access_key
				access_secret = vals.get("access_secret") if vals.get("access_secret") else question.access_secret
				member_id = 0
				member_id, nick = fetch_member_id_and_nick(_get_url(BASE_URL, member.get("test")),consumer_key, consumer_secret, access_key,access_secret)
				vals["member_id"] = member_id;
				vals["name"] = nick;
		except Exception as ex:
			raise osv.except_osv(_('Unable to connect to the Trademe. Probably invalid keys.'), _(ex.message))
		res = super(TMMembers, self).write(cr, uid, ids, vals, context=context)
		return res;
	

class TMListing(osv.osv):
	def _get_concate(self, cr, uid, ids, field_name, arg, context=None):
			records=self.browse(cr,uid,ids)
			result={}
			for r in records:
				result[r.id]= _get_url(UI_BASE_URL, r.member.test)+'Browse/Listing.aspx?id='+str(r.listing_id)
			return result
	
	_name = 'tmerp.listing'
	_columns = {
		'name': fields.char('Listing Name', required=True, size=100),
		'listing_id': fields.char('Listing Id', required=True),
		'member': fields.many2one('tmerp.members', 'Account'),
		'listing_url': fields.function(_get_concate, method=True, string='URL', type='char'),
		
	}
	
class TMQuestions(osv.osv):
	_name = 'tmerp.questions'
	_columns = {
		'comment': fields.text('Comment', required=True),
		'question_id': fields.char('Question Id', required=True, readonly=True),
		'asking_member_name': fields.char('Asking Member', required=True),
		'listing': fields.many2one('tmerp.listing', 'Listing'),
		'member': fields.many2one('tmerp.members', 'Account'),
		'is_replied': fields.boolean('Is Replied', readonly=True),
		'reply': fields.text('Reply', size=4096),
	};
	def write(self, cr, uid, ids, vals, context=None):
		_logger.info(str.format("Posing reply on the for the question {0}, data {1}",ids,vals ));
		reply = vals.get('reply')
		if reply is not None and reply is not False:
			list = self.pool.get('tmerp.questions').browse(cr, uid, ids)
			if len(list) > 0: 
				question = list[0];
				if question.is_replied is None or not question.is_replied:
					listing = question.listing
					question_id= question.question_id;
					member = listing.member
					_logger.info(str.format("Posing reply for listing {0}, question id {1}, member {2}, Comment:{3}",listing.listing_id, question_id, member.name, reply));
					try:
						reply_to_question(_get_url(BASE_URL, member.test),member.consumer_key,member.consumer_secret,member.access_key,member.access_secret, listing.listing_id, question_id, reply)
						vals['is_replied'] = True
					except Exception as ex:
						if str(ex.message).find("Your response has already been recorded")>=0:
							vals['is_replied'] = True
							vals['reply'] = "REPLIED FROM Trademe Website"
							super(TMQuestions, self).write(cr, uid, ids, vals, context=context)
							cr.commit()
							raise osv.except_osv(_('Unable to answer question'), _("Question is already answered from the Trademe UI."))
						else:
							raise osv.except_osv(_('Unable to answer question'), _(ex.message))
				else:
					raise osv.except_osv(_('Unable to answer question'), _("Question is already answered."))
		res = super(TMQuestions, self).write(cr, uid, ids, vals, context=context)
		return res

class TMRun(osv.osv):
	_name = 'tmerp.action.listing'
	lock = threading.Lock()
	
	def synchronized(method):
		def new_method(self, *arg, **kws):
			with self.lock:
				return method(self, *arg, **kws)
		return new_method
	
	@synchronized
	def _fetch_members_listing(self, cr, uid, context=None):
		_logger.info("Executing Trademe scheduler : Fetch All Listings");
		#_logger.info("Getting all registered members in OpenERP");
		cr.execute('select id from tmerp_members where is_enabled = true order by id')
		ids = map(lambda x: x[0], cr.fetchall())
		_logger.info(str.format("Total {0} registered members found in OpenERP",len(ids)));
		for member in self.pool.get('tmerp.members').browse(cr, uid, ids):
			if not member.is_enabled:
				#_logger.info(str.format("Not fetching listing as Member {0} is disabled.", member.name));
				continue
			try:
				_logger.info(str.format("Getting listing for member {0}", member.name));
				listings = fetch_members_listing(_get_url(BASE_URL, member.test),member.consumer_key,member.consumer_secret,member.access_key,member.access_secret,member.member_id)
				_logger.info(str.format("Total {0} listings found for member {1}:", len(listings), member.name))
				for listing in listings:
					listing_id = str(listing.get('ListingId'))
					cr.execute('select id from tmerp_listing where listing_id=%s and member=%s order by id', [listing_id, member.id])
					exitingIds = map(lambda x: x[0], cr.fetchall())
					if(len(exitingIds)<=0):
						listing_id = self.pool.get('tmerp.listing').create(cr, uid,{ 'name': listing.get('Title'), 'listing_id' : str(listing.get('ListingId')), 'member': member.id}, context=context)
						#_logger.info(str.format("Created new listing:{0} for member {1}, Listing: {2}",listing_id, member.name, listing.get('Title')))
					#else:
						#_logger.info(str.format("No need to create listing for listing id {0}, as record with id {1} already exists in database for member {2}.",listing_id, str(exitingIds[0]), member.name));
			except:
				ex = sys.exc_info()[0]
				print ex
				#_logger.info(str.format("Unable to get the member/listing data for member {0}, Error:{1}", member.name,ex.message),ex);
		_logger.info("Completed Executing Trademe scheduler : Fetch All Listings");
		return True;
		
	def _fetch_un_questions(self, cr, uid, context=None):
		_logger.info("Executing Trademe scheduler : Fetch Unanswered Questions");		
		_logger.info("Getting all registered members in OpenERP");
		cr.execute('select id from tmerp_members where is_enabled = true order by id')
		mids = map(lambda x: x[0], cr.fetchall())
		_logger.info(str.format("Total {0} registered members found in OpenERP",len(mids)));
		for member in self.pool.get('tmerp.members').browse(cr, uid, mids):
			if not member.is_enabled:
				_logger.info(str.format("Not fetching Questions as Member {0} is disabled.", member.name));
				continue
			try:
				_logger.info(str.format("Getting unanswered questions for member {0}", member.name));
				questinons = fetch_all_unanswered_questions(_get_url(BASE_URL, member.test), member.consumer_key,member.consumer_secret,member.access_key,member.access_secret);
				print "-------------------------------------------------------------------------------------------------------"
				print questinons
				_logger.info(str.format("Total {0} unanswered questions retrieved for member {1}", len(questinons),member.name));
			except:
				ex = sys.exc_info()[0]
				_logger.info(str.format("Unable to get the unanswered questions data for member {0}, Error:{1}", member.name, ex.message),ex);
			
			_logger.info(str.format("Getting all listings of member {0} in OpenERP", member.name));
			cr.execute(str.format('select id from tmerp_listing where member = {0} order by id',member.id))
			ids = map(lambda x: x[0], cr.fetchall())
			_logger.info(str.format("Total {0} listings found for member {1} in OpenERP",len(ids), member.name));
			object_dict = dict((str(x.listing_id), x) for x in self.pool.get('tmerp.listing').browse(cr, uid, ids))
			questionListingIds = map(lambda x: str(x.get('ListingId')), questinons)
			missing = set(questionListingIds)-set(object_dict.keys())
			_logger.info(missing)
			#get all members listing as there is some question which is having listing which is not there in database
			if (len(missing)>0):
				_logger.info(str.format("Lising with ids {0} are not yet synced. Forcing listing sync.", missing));
				self._fetch_members_listing(cr=cr, uid=uid, context=context)
				#refresh the list
				cr.execute(str.format('select id from tmerp_listing where member = {0} order by id',member.id))
				ids = map(lambda x: x[0], cr.fetchall())
				_logger.info(str.format("Total {0} listings found for member {1} in OpenERP",len(ids), member.name));
				object_dict = dict((str(x.listing_id), x) for x in self.pool.get('tmerp.listing').browse(cr, uid, ids))
			try:
				for que in questinons:
					listing_id = str(que.get('ListingId'));
					try:
						listing = dict();
						if(not listing_id in object_dict):
							_logger.info(str.format("Listing {0} is still not available. Creating dummy listing entry",listing_id));
							internal_listing_id = self.pool.get('tmerp.listing').create(cr, uid,{ 'name': 'dummy listing', 'listing_id' : listing_id, 'member': member.id}, context=context)
							listing.listing_id = listing_id 
							_logger.info(str.format("Created new listing:{0} for member {1}, Listing: {2}",listing_id, str(member.id), listing.get('Title')))
						else:
							listing = object_dict[listing_id];
						question_id = str(que.get('ListingQuestionId'))
						cr.execute('select id from tmerp_questions where question_id=%s and listing=%s order by id', [question_id, listing.id])
						exitingIds = map(lambda x: x[0], cr.fetchall())
						if(len(exitingIds)<=0):
							que_id = self.pool.get('tmerp.questions').create(cr, uid,{ 'comment': que.get('Comment'), 'listing' : listing.id, 'member' : member.id, 'asking_member_name':(str(que.get('AskingMember').get('Nickname'))+' - '+str(que.get('AskingMember').get('MemberId'))), 'is_replied':False, 'reply':'', 'question_id':question_id}, context=context)
							_logger.info(str.format("Created new unanswered question:{0} for listing question id {1} and Listing: {2}",que_id, question_id, listing_id))
						else:
							_logger.info(str.format("No need to create unanswered question for listing id {0}, as record with id {1} for question id {2} already exists in database .",listing_id, str(exitingIds[0]), question_id));
					except:
						ex = sys.exc_info()[0]
						_logger.info(str.format("Unable to process unanswered questions of listing {0}, Error:{1}", listing_id, ex.message),ex);
			except:
				ex = sys.exc_info()[0]
				_logger.info(str.format("Unable to process polling of unanswered questions Error:{0}", ex.message),ex);
			_logger.info("Completed Executing Trademe scheduler : Fetch Unanswered Questions");
		return True;

TMMembers()
TMListing()
TMQuestions()
TMRun()

